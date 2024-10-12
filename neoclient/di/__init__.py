import dataclasses
import inspect
from typing import Any, Final, Mapping, Optional, Type, TypeVar

import httpx
from di import Container, SolvedDependent, bind_by_type
from di.api.dependencies import DependentBase
from di.api.executor import SupportsSyncExecutor
from di.api.providers import DependencyProvider, DependencyProviderType
from di.dependent import Dependent
from di.executors import SyncExecutor
from pydantic import BaseModel
from pydantic.fields import FieldInfo, ModelField, Undefined

from neoclient import utils
from neoclient.di.dependencies import DEPENDENCIES
from neoclient.di.inference import infer_dependency
from neoclient.params import (
    AllStateParameter,
    CookiesParameter,
    HeadersParameter,
    Parameter,
    QueryParameter,
    QueryParamsParameter,
    RequestParameter,
    ResponseParameter,
    URLParameter,
)
from neoclient.validation import create_func_model, parameter_to_model_field

from ..models import (
    URL,
    Cookies,
    Headers,
    QueryParams,
    Request,
    RequestOpts,
    Response,
    State,
)

T = TypeVar("T")

EXECUTOR: Final[SupportsSyncExecutor] = SyncExecutor()


def _bind_hook(
    param: Optional[inspect.Parameter], dependent: DependentBase[Any]
) -> Optional[DependentBase[Any]]:
    print("_bind_hook", repr(param), dependent)

    if param is None:
        return None

    if not isinstance(param.annotation, type):
        raise NotImplementedError  # TODO

    # TEMP
    if param.annotation is RequestOpts:
        return Dependent(RequestOpts, wire=False)

    dependency: type = param.annotation

    # TODO: Improve this check (allow subclasses)
    if dependency in DEPENDENCIES:
        provider = DEPENDENCIES[dependency]

        # if len(providers) != 1:
        #     raise NotImplementedError  # TODO

        # return Dependent(providers[0])
        return Dependent(provider)
        # return None

    # Attempt inference
    inferred = infer_dependency(param)

    if inferred is not None:
        return Dependent(inferred)

    raise Exception(f"No provider registered for {param.annotation!r}")


def _solve_and_execute(
    container: Container,
    dependent: DependencyProviderType[T],
    values: Mapping[DependencyProvider, Any] | None = None,
    *,
    use_cache: bool = True,
) -> T:
    print("solve - start")
    solved: SolvedDependent[T] = container.solve(
        Dependent(dependent, use_cache=use_cache),
        scopes=(None,),
    )
    print("solve - end")

    with container.enter_scope(None) as state:
        print("execute - start")
        tmp = solved.execute_sync(
            executor=EXECUTOR,
            state=state,
            values=values,
        )
        print("execute - end")
        return tmp


# TEMP
request_container = Container()
request_container.bind(_bind_hook)


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
