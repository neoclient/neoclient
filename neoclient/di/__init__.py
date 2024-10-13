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

from neoclient.di.dependencies import DEPENDENCIES
from neoclient.di.inference import infer_dependency
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

        # If there's no parameter, than a dependent is already known.
        # As a dependent is already known, we don't need to anything.
        if param is None:
            return None
        
        model_field: ModelField = parameter_to_model_field(param)
        field_info: FieldInfo = model_field.field_info

        print(repr(model_field), repr(model_field.annotation)) # TEMP

        if not isinstance(param.annotation, type):
            raise NotImplementedError  # TODO

        # TEMP
        if param.annotation in (RequestOpts, Response, httpx.Response):
            return None # these should already be stubbed

        dependency: type = param.annotation

        # TODO: Improve this check (allow subclasses?)
        if dependency in dependencies:
            provider = dependencies[dependency]
            return Dependent(provider)

        inferred = infer_dependency(param, profile)

        if inferred is not None:
            return Dependent(inferred)

        raise WiringError(
            f"No dependency provider of type {param.annotation!r} found for parameter {param.name!r}",
            [],
        )

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
