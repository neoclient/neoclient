import inspect
from typing import (
    Any,
    Callable,
    MutableMapping,
    MutableSequence,
    NoReturn,
    Optional,
    TypeVar,
)

from di import Container
from di.api.dependencies import DependentBase
from di.api.providers import DependencyProvider, DependencyProviderType
from di.dependent import Dependent
from di.executors import SyncExecutor
from httpx import Headers, QueryParams

from neoclient.models import RequestOpts

C = TypeVar("C", bound=Callable[..., Any])

DEPENDENCIES: MutableMapping[type, MutableSequence[DependencyProviderType[type]]] = {}


def not_wirable() -> NoReturn:
    raise Exception("Not wirable")


def bean(func: C, /) -> C:
    dependency: Any = inspect.signature(func).return_annotation

    assert isinstance(dependency, type)

    DEPENDENCIES.setdefault(dependency, []).append(func)

    return func


@bean
def _headers(request: RequestOpts, /) -> Headers:
    return request.headers


@bean
def _params(request: RequestOpts, /) -> QueryParams:
    return request.params


container = Container()

# dependency: type
# providers: Sequence[DependencyProviderType[type]]
# for dependency, providers in DEPENDENCIES.items():
#     if len(providers) != 1:
#         raise NotImplementedError  # TODO

#     provider = providers[0]

#     container.bind(bind_by_type(Dependent(provider), dependency))

# TEMP
# container.bind(bind_by_type(Dependent(RequestOpts, wire=False), RequestOpts))


def infer_dependency(parameter: inspect.Parameter, /) -> Optional[DependencyProvider]:
    if parameter.name == "headers":
        return _headers
    elif parameter.name == "params":
        return _params

    return None


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
        providers = DEPENDENCIES[dependency]

        if len(providers) != 1:
            raise NotImplementedError  # TODO

        return Dependent(providers[0])
        # return None

    # Attempt inference
    inferred = infer_dependency(param)

    if inferred is not None:
        return Dependent(inferred)

    raise Exception(f"No provider registered for {param.annotation!r}")


# TEMP
container.bind(_bind_hook)


def my_dependency(params):
    return params


executor = SyncExecutor()
solved = container.solve(
    Dependent(my_dependency),
    scopes=(None,),
)

with container.enter_scope(None) as state:
    d = solved.execute_sync(
        executor=executor,
        state=state,
        values={
            RequestOpts: RequestOpts(
                "GET", "/", params={"sort": "asc"}, headers={"x-name": "bob"}
            )
        },
    )
