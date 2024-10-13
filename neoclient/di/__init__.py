import dataclasses
import inspect
from typing import Any, Final, Mapping, Optional, TypeVar

import httpx
import rich.pretty
from di import Container, SolvedDependent, bind_by_type
from di.api.dependencies import DependentBase
from di.api.executor import SupportsSyncExecutor
from di.api.providers import DependencyProvider, DependencyProviderType
from di.dependent import Dependent
from di.exceptions import WiringError
from di.executors import SyncExecutor
from pydantic.fields import FieldInfo, ModelField, Undefined

from neoclient import utils
from neoclient.di.dependencies import DEPENDENCIES
from neoclient.di.inference import infer_dependency
from neoclient.params import Parameter, QueryParameter, QueryParamsParameter
from neoclient.validation import parameter_to_model_field

from ..models import RequestOpts, Response
from .enums import Profile

T = TypeVar("T")

EXECUTOR: Final[SupportsSyncExecutor] = SyncExecutor()


def _build_bind_hook(profile: Profile, /):
    dependencies = DEPENDENCIES[profile]

    def _bind_hook(
        param: Optional[inspect.Parameter], dependent: DependentBase[Any]
    ) -> Optional[DependentBase[Any]]:
        print("_bind_hook", repr(param), dependent)

        # If there's no parameter, then a dependent is already known.
        # As a dependent is already known, we don't need to anything.
        if param is None:
            return None

        # The parameter needs to be stubbed, as a value will be provided
        # during execution.
        if param.annotation in (RequestOpts, Response, httpx.Response):
            return None  # these should already be stubbed

        model_field: ModelField = parameter_to_model_field(param)
        field_info: FieldInfo = model_field.field_info

        # The aim of the game is to convert an inspect Parameter into a
        # neoclient Parameter.
        parameter: Parameter

        print(repr(model_field), repr(model_field.annotation), repr(field_info))  # TEMP

        # 1. Parameter metadata exists! Let's use that.
        if isinstance(field_info, Parameter):
            parameter = field_info
        # n. Parameter is variadic, special case. (deprecated: di doesn't like.)
        # elif param.kind in (
        #     inspect.Parameter.VAR_POSITIONAL,
        #     inspect.Parameter.VAR_KEYWORD,
        # ):
        #     parameter = QueryParamsParameter()
        # n. Parameter name matches a path parameter (during composition only)
        # elif profile is Profile.REQUEST and param.name in path_params:
        #     ...
        # n. Parameter type is a known dependency (TODO: Support subclasses)
        elif isinstance(param.annotation, type) and param.annotation in dependencies:
            return Dependent(
                dependencies[param.annotation]
            )  # TODO: Use a neoclient Depends parameter?
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
        # n. Inference failed (shouldn't happen?)
        # else:
        #     raise NotImplementedError  # TODO

        # Create a clone of the parameter so that any mutations do not affect the original
        parameter_clone: Parameter = dataclasses.replace(parameter)

        parameter_clone.prepare(model_field)

        print(repr(parameter_clone), parameter_clone.alias)

        return Dependent(parameter_clone.to_dependent())

        # if not isinstance(param.annotation, type):
        #     raise NotImplementedError  # TODO

        # # TEMP
        # if param.annotation in (RequestOpts, Response, httpx.Response):
        #     return None # these should already be stubbed

        # dependency: type = param.annotation

        # # TODO: Improve this check (allow subclasses?)
        # if dependency in dependencies:
        #     provider = dependencies[dependency]
        #     return Dependent(provider)

        # inferred = infer_dependency(param, profile)

        # if inferred is not None:
        #     return Dependent(inferred)

        # raise WiringError(
        #     f"No dependency provider of type {param.annotation!r} found for parameter {param.name!r}",
        #     [],
        # )

    return _bind_hook


def _solve_and_execute(
    container: Container,
    dependent: DependencyProviderType[T],
    values: Mapping[DependencyProvider, Any] | None = None,
    *,
    use_cache: bool = True,
) -> T:
    # print("solve - start")
    solved: SolvedDependent[T] = container.solve(
        Dependent(dependent, use_cache=use_cache),
        scopes=(None,),
    )
    # rich.pretty.pprint(solved.dag)
    # print("solve - end")

    with container.enter_scope(None) as state:
        # print("execute - start")
        tmp = solved.execute_sync(
            executor=EXECUTOR,
            state=state,
            values=values,
        )
        # print("execute - end")
        return tmp


# TEMP
request_container = Container()
request_container.bind(bind_by_type(Dependent(RequestOpts, wire=False), RequestOpts))
request_container.bind(_build_bind_hook(Profile.REQUEST))
response_container = Container()
response_container.bind(bind_by_type(Dependent(RequestOpts, wire=False), RequestOpts))
response_container.bind(
    bind_by_type(Dependent(httpx.Response, wire=False), httpx.Response, covariant=True)
)
response_container.bind(_build_bind_hook(Profile.RESPONSE))


# inject, solve, execute, resolve, handle
def inject_request(
    dependent: DependencyProviderType[T],
    request: RequestOpts,
    *,
    use_cache: bool = True,
) -> T:
    return _solve_and_execute(
        request_container,
        dependent,
        {RequestOpts: request},
        use_cache=use_cache,
    )


def inject_response(
    dependent: DependencyProviderType[T],
    response: Response,
    *,
    use_cache: bool = True,
) -> T:
    return _solve_and_execute(
        response_container,
        dependent,
        {
            Response: response,
            httpx.Response: response,  # Included as `di` doesn't seem to respect covariance
        },
        use_cache=use_cache,
    )
