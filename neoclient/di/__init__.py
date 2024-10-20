import dataclasses
import inspect
from typing import Any, Callable, Final, Mapping, MutableMapping, Optional, Set, Tuple, TypeVar, Union

import httpx
from di import Container, SolvedDependent, bind_by_type
from di.api.dependencies import DependentBase
from di.api.executor import SupportsSyncExecutor
from di.api.providers import DependencyProvider, DependencyProviderType
from di.dependent import Dependent
from di.exceptions import WiringError
from di.executors import SyncExecutor
from pydantic import BaseModel
from pydantic.fields import FieldInfo, ModelField, Undefined, UndefinedType

from neoclient import api, utils
from neoclient.composition import get_fields, validate_fields
from neoclient.di.dependencies import DEPENDENCIES
from neoclient.params import Parameter, PathParameter, QueryParameter
from neoclient.validation import ValidatedFunction, parameter_to_model_field

from ..models import RequestOpts, Response
from .enums import Profile

# No inference:
# * Parameter metadata exists, use that. (e.g. headers = Headers())
# Inference:
# 1. Parameter name matches a path parameter, assume a path param
# 2. Type is a known dependency (e.g. headers: Headers), no inference needed.
# 3. Type indicates a body parameter (e.g. user: User), treat as body parameter.
# 4. Assume query parameter
# Don't do:
# * Infer by name? Only do if not typed? Only do for select few? (FastAPI doesn't do this.)


T = TypeVar("T")

EXECUTOR: Final[SupportsSyncExecutor] = SyncExecutor()

DO_NOT_AUTOWIRE: Set[type] = {RequestOpts, Response, httpx.Response}


def _build_bind_hook(subject: Union[RequestOpts, Response], /):
    def _bind_hook(
        param: Optional[inspect.Parameter], dependent: DependentBase[Any]
    ) -> Optional[DependentBase[Any]]:
        # print("_bind_hook", repr(param), dependent)

        # If there's no parameter, then a dependent is already known.
        # As a dependent is already known, we don't need to anything.
        if param is None:
            return None

        # The parameter needs to be stubbed, as a value will be provided
        # during execution.
        if param.annotation in DO_NOT_AUTOWIRE:
            return None  # these should already be stubbed

        parameter: Parameter = infer(param, subject)

        # print(repr(parameter_clone), parameter_clone.alias)

        return Dependent(parameter.get_resolution_dependent())

        # raise WiringError(
        #     f"No dependency provider of type {param.annotation!r} found for parameter {param.name!r}",
        #     [],
        # )

    return _bind_hook


def _solve(
    container: Container,
    dependent: DependencyProviderType[T],
    *,
    use_cache: bool = True,
) -> SolvedDependent[T]:
    return container.solve(
        Dependent(dependent, use_cache=use_cache),
        scopes=(None,),
    )


def _execute(
    container: Container,
    solved: SolvedDependent[T],
    values: Mapping[DependencyProvider, Any] | None = None,
) -> T:
    with container.enter_scope(None) as state:
        return solved.execute_sync(
            executor=EXECUTOR,
            state=state,
            values=values,
        )


def _solve_and_execute(
    container: Container,
    dependent: DependencyProviderType[T],
    values: Mapping[DependencyProvider, Any] | None = None,
    *,
    use_cache: bool = True,
) -> T:
    solved: SolvedDependent[T] = _solve(container, dependent, use_cache=use_cache)

    return _execute(container, solved, values)


# TEMP
# composition_container = Container()
request_container = Container()
request_container.bind(bind_by_type(Dependent(RequestOpts, wire=False), RequestOpts))
response_container = Container()
response_container.bind(bind_by_type(Dependent(RequestOpts, wire=False), RequestOpts))
response_container.bind(
    bind_by_type(Dependent(httpx.Response, wire=False), httpx.Response, covariant=True)
)


# inject, solve, execute, resolve, handle
def inject_request(
    dependent: DependencyProviderType[T],
    request: RequestOpts,
    *,
    use_cache: bool = True,
) -> T:
    with request_container.bind(_build_bind_hook(request)):
        solved: SolvedDependent[T] = _solve(
            request_container, dependent, use_cache=use_cache
        )

    return _execute(
        request_container,
        solved,
        {
            RequestOpts: request,
        },
    )


def inject_response(
    dependent: DependencyProviderType[T],
    response: Response,
    *,
    use_cache: bool = True,
) -> T:
    with response_container.bind(_build_bind_hook(response)):
        solved: SolvedDependent[T] = _solve(
            response_container, dependent, use_cache=use_cache
        )

    return _execute(
        response_container,
        solved,
        {
            Response: response,
            # Included as `di` doesn't seem to respect covariance
            httpx.Response: response,
        },
    )


def infer(
    param: inspect.Parameter, subject: Union[RequestOpts, Response]
) -> Parameter:
    profile: Profile = (
        Profile.REQUEST if isinstance(subject, RequestOpts) else Profile.RESPONSE
    )
    dependencies = DEPENDENCIES[profile]

    model_field: ModelField = parameter_to_model_field(param)
    field_info: FieldInfo = model_field.field_info

    # The aim of the game is to convert an inspect Parameter into a
    # neoclient Parameter.
    parameter: Parameter

    # print(repr(model_field), repr(model_field.annotation), repr(field_info))  # TEMP

    path_params: Set[str] = (
        utils.parse_format_string(str(subject.url))
        if profile is Profile.REQUEST
        else set()
    )

    # 1. Parameter metadata exists! Let's use that.
    if isinstance(field_info, Parameter):
        parameter = field_info
    # n. Parameter name matches a path parameter (during composition only)
    elif param.name in path_params:
        parameter = PathParameter(
            alias=param.name,
            default=utils.get_default(field_info),
        )
    # n. Parameter type is a known dependency (TODO: Support subclasses)
    elif isinstance(param.annotation, type) and param.annotation in dependencies:
        raise NotImplementedError
        # # parameter = DependencyParameter(...)
        # return Dependent(
        #     dependencies[param.annotation]
        # )  # TODO: Use a neoclient Depends parameter?
    # n. Parameter type indicates a body parameter
    # ...
    # n. Otherwise, assume a query parameter
    else:
        # Note: What if the type is non-primitive (e.g. foo: Foo),
        # do we always want to assume a query parameter?
        # What does FastAPI do?
        parameter = QueryParameter(
            default=utils.get_default(field_info),
        )

    # Create a clone of the parameter so that any mutations do not affect the original
    parameter_clone: Parameter = dataclasses.replace(parameter)

    parameter_clone.prepare(model_field)

    return parameter_clone


def get_parameters(
    func: Callable, request: RequestOpts
) -> Mapping[str, Tuple[Any, Parameter]]:
    validated_function: ValidatedFunction = ValidatedFunction(func)

    parameters: Mapping[str, inspect.Parameter] = (
        validated_function.signature.parameters
    )

    # print(parameters)

    metas: MutableMapping[str, Tuple[Any, Parameter]] = {}

    # field_name: str
    # model_field: ModelField
    # for field_name, model_field in validated_function.model.__fields__.items():
    #     raw_parameter: inspect.Parameter = parameters[field_name]
    #     field_info: FieldInfo = model_field.field_info
    #     parameter: Parameter

    #     print(field_name, raw_parameter, field_info)

    #     metas[field_name] = (model_field.annotation, parameter_clone)

    parameter: inspect.Parameter
    for parameter in parameters.values():
        annotation: Union[Any, UndefinedType] = (
            parameter.annotation
            if parameter.annotation is not inspect.Parameter.empty
            else Undefined
        )
        meta: Parameter = infer(parameter, request)

        metas[parameter.name] = (annotation, meta)

    return metas


def compose(
    func: Callable,
    request: RequestOpts,
    # TODO: Use *args and **kwargs instead?
    args: Tuple[Any, ...],
    kwargs: Mapping[str, Any],
) -> None:
    arguments: Mapping[str, Any] = api.bind_arguments(func, args, kwargs)
    fields: Mapping[str, Tuple[Any, Parameter]] = get_parameters(func, request)

    # print(arguments, fields)

    # TODO: Do we still need/want to do this?
    # Validate that the fields are acceptable
    validate_fields(fields)

    model: BaseModel = api.create_model(func.__name__, fields, arguments)

    # By this stage the arguments have been validated
    validated_arguments: Mapping[str, Any] = model.dict()

    # print(validated_arguments)

    field_name: str
    parameter: Parameter
    for field_name, (_, parameter) in fields.items():
        argument: Any = validated_arguments[field_name]

        dependent: DependencyProviderType[None] = parameter.get_composition_dependent(argument)

        # do_compose(parameter, request, argument)

        with request_container.bind(_build_bind_hook(request)):
            solved: SolvedDependent[None] = _solve(
                request_container,
                dependent,
                # TODO: Make this configurable?
                use_cache=True,
            )

        _execute(
            request_container,
            solved,
            {
                RequestOpts: request,
            },
        )
