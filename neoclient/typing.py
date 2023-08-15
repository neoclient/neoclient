from abc import abstractmethod
from typing import Any, Callable, Protocol, Sequence, TypeVar, runtime_checkable

import mediate
from typing_extensions import TypeAlias

from .models import ClientOptions, PreRequest, Request, Response

__all__: Sequence[str] = (
    "AnyCallable",
    "CallNext",
    "Decorator",
    "Dependency",
    "ClientConsumer",
    "Composer",
    "Consumer",
    "Function",
    "RequestConsumer",
    "RequestResolver",
    "ResponseResolver",
    "Supplier",
    "SupportsConsumeClient",
    "SupportsConsumeRequest",
    "SupportsResolveRequest",
    "SupportsResolveResponse",
)

T = TypeVar("T")
T_contra = TypeVar("T_contra", contravariant=True)
T_co = TypeVar("T_co", covariant=True)
R_co = TypeVar("R_co", covariant=True)

AnyCallable: TypeAlias = Callable[..., Any]
Dependency: TypeAlias = AnyCallable

MiddlewareCallable: TypeAlias = mediate.protocols.MiddlewareCallable[Request, Response]


class CallNext(Protocol):
    def __call__(self, request: Request, /) -> Response:
        ...


class Decorator(Protocol[T]):
    @abstractmethod
    def __call__(self, target: T, /) -> T:
        ...


class Supplier(Protocol[T_co]):
    def __call__(self) -> T_co:
        ...


class Consumer(Protocol[T_contra]):
    def __call__(self, t: T_contra, /) -> None:
        ...


class Function(Protocol[T_contra, R_co]):
    def __call__(self, t: T_contra, /) -> R_co:
        ...


class ResponseResolver(Function[Response, T_co], Protocol[T_co]):
    pass


class RequestResolver(Function[PreRequest, T_co], Protocol[T_co]):
    pass


class RequestConsumer(Consumer[PreRequest], Protocol):
    pass


class ClientConsumer(Consumer[ClientOptions], Protocol):
    pass


class Composer(Protocol):
    def compose(self, request: PreRequest, argument: Any, /) -> None:
        ...


@runtime_checkable
class SupportsConsumeRequest(Protocol):
    @abstractmethod
    def consume_request(self, request: PreRequest, /) -> None:
        ...


@runtime_checkable
class SupportsConsumeClient(Protocol):
    @abstractmethod
    def consume_client(self, client: ClientOptions, /) -> None:
        ...


@runtime_checkable
class SupportsResolveRequest(Protocol[T_co]):
    @abstractmethod
    def resolve_request(self, request: PreRequest, /) -> T_co:
        ...


@runtime_checkable
class SupportsResolveResponse(Protocol[T_co]):
    @abstractmethod
    def resolve_response(self, response: Response, /) -> T_co:
        ...
