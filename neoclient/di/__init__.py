import dataclasses
import inspect
from typing import Any, Final, Mapping, Optional, Set, TypeVar, Union

import httpx
from di import Container, SolvedDependent, bind_by_type
from di.api.dependencies import DependentBase
from di.api.executor import SupportsSyncExecutor
from di.api.providers import DependencyProvider, DependencyProviderType
from di.dependent import Dependent
from di.exceptions import WiringError
from di.executors import SyncExecutor
from pydantic.fields import FieldInfo, ModelField

from neoclient import utils
from neoclient.di.dependencies import DEPENDENCIES
from neoclient.params import Parameter, QueryParameter
from neoclient.validation import parameter_to_model_field

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


# # @dataclasses.dataclass(unsafe_hash=True, init=False)
# @dataclasses.dataclass(unsafe_hash=True)
# class NoParameter:  # (Parameter):
#     """
#     Parameter class for when no parameter metadata was specified.

#     This parameter will perform *inference* and morph into an appropriate
#     parameter based on the subject of the injection.
#     """

#     parameter: inspect.Parameter
#     profile: Profile

#     # def __init__(self, parameter: inspect.Parameter, profile: Profile) -> None:
#     #     super().__init__()

#     #     self.parameter = parameter
#     #     self.profile = profile

#     # def compose(self, request: RequestOpts, argument: Any, /) -> None:
#     #     raise CompositionError(f"Parameter {type(self)!r} is not composable")

#     # def resolve_response(self, response: Response, /) -> Any:
#     #     raise ResolutionError(
#     #         f"Parameter {type(self)!r} is not resolvable for type {Response!r}"
#     #     )

#     # def resolve_request(self, request: RequestOpts, /) -> Any:
#     #     raise ResolutionError(
#     #         f"Parameter {type(self)!r} is not resolvable for type {RequestOpts!r}"
#     #     )

#     def to_dependent(self) -> DependencyProviderType[Any]:
#         if self.profile is Profile.REQUEST:

#             def apply(request: RequestOpts, /):
#                 raise NotImplementedError("Inference logic here?")

#             return apply
#         else:
#             raise NotImplementedError  # TODO

#     def prepare(self, model_field: ModelField, /) -> None:
#         return


# def dep_no_param_req(request: RequestOpts, /) -> Any:
#     raise NotImplementedError


# def dep_no_param_resp(response: Response, /) -> Any:
#     raise NotImplementedError

# def _do_infer(subject: Union[RequestOpts, Response], /):
#     ...

# def dep_no_param(parameter: inspect.Parameter, /):
#     def f(profile: Profile, container: Container, /):
#         cls = RequestOpts if profile is Profile.REQUEST else Response


#         # return _solve_and_execute(container, Dependent(cls))

#     return f


def _build_bind_hook(subject: Union[RequestOpts, Response], /):
    profile: Profile = (
        Profile.REQUEST if isinstance(subject, RequestOpts) else Profile.RESPONSE
    )
    dependencies = DEPENDENCIES[profile]

    def _bind_hook(
        param: Optional[inspect.Parameter], dependent: DependentBase[Any]
    ) -> Optional[DependentBase[Any]]:
        # print("_bind_hook", repr(param), dependent)
        # input()

        # If there's no parameter, then a dependent is already known.
        # As a dependent is already known, we don't need to anything.
        if param is None:
            return None

        # The parameter needs to be stubbed, as a value will be provided
        # during execution.
        if param.annotation in DO_NOT_AUTOWIRE:
            return None  # these should already be stubbed

        model_field: ModelField = parameter_to_model_field(param)
        field_info: FieldInfo = model_field.field_info

        # The aim of the game is to convert an inspect Parameter into a
        # neoclient Parameter.
        parameter: Parameter

        # print(repr(model_field), repr(model_field.annotation), repr(field_info))  # TEMP

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
        # else:
            # parameter = NoParameter(parameter=param, profile=profile)
            # return Dependent(
            #     {
            #         Profile.REQUEST: dep_no_param_req,
            #         Profile.RESPONSE: dep_no_param_resp,
            #     }[profile]
            # )
            # return Dependent(dep_no_param)
            # raise NotImplementedError

        # Create a clone of the parameter so that any mutations do not affect the original
        parameter_clone: Parameter = dataclasses.replace(parameter)

        parameter_clone.prepare(model_field)

        # print(repr(parameter_clone), parameter_clone.alias)

        return Dependent(parameter_clone.to_dependent())

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
request_container = Container()
request_container.bind(bind_by_type(Dependent(RequestOpts, wire=False), RequestOpts))
# request_container.bind(_build_bind_hook(Profile.REQUEST))
response_container = Container()
response_container.bind(bind_by_type(Dependent(RequestOpts, wire=False), RequestOpts))
response_container.bind(
    bind_by_type(Dependent(httpx.Response, wire=False), httpx.Response, covariant=True)
)
# response_container.bind(_build_bind_hook(Profile.RESPONSE))


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
            # Environment
            # Profile: Profile.REQUEST,
            # Container: request_container,
            # SolvedDependent: solved,
            # Subject
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
            # Environment
            # Profile: Profile.RESPONSE,
            # Container: request_container,
            # SolvedDependent: solved,
            # Subject
            Response: response,
            httpx.Response: response,  # Included as `di` doesn't seem to respect covariance
        },
    )
