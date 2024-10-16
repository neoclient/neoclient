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


def _build_bind_hook(subject: Union[RequestOpts, Response], /):
    profile: Profile = (
        Profile.REQUEST if isinstance(subject, RequestOpts) else Profile.RESPONSE
    )
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
