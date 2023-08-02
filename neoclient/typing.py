from typing import Any, Protocol, Sequence, TypeVar, runtime_checkable

from .models import ClientOptions, PreRequest, Request, Response

__all__: Sequence[str] = (
    "CallNext",
    "Decorator",
    "ClientConsumer",
    "Composer",
    "RequestConsumer",
    "ResponseResolver",
    "Supplier",
    "SupportsClientConsumer",
    "SupportsRequestConsumer",
)

T = TypeVar("T")
T_contra = TypeVar("T_contra", contravariant=True)
T_co = TypeVar("T_co", covariant=True)
R_co = TypeVar("R_co", covariant=True)


class CallNext(Protocol):
    def __call__(self, request: Request, /) -> Response:
        ...


class Decorator(Protocol[T]):
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


class Composer(Protocol):
    def compose(self, request: PreRequest, argument: Any, /) -> None:
        ...


class RequestConsumer(Consumer[PreRequest], Protocol):
    pass


@runtime_checkable
class SupportsRequestConsumer(Protocol):
    def consume_request(self, request: PreRequest, /) -> None:
        ...


class ClientConsumer(Consumer[ClientOptions], Protocol):
    pass


@runtime_checkable
class SupportsClientConsumer(Protocol):
    def consume_client(self, client: ClientOptions, /) -> None:
        ...
