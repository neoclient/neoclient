from typing import Any, Protocol, Sequence, TypeVar

from .models import RequestOptions, Request, Response

__all__: Sequence[str] = (
    "CallNext",
    "Composer",
    "RequestConsumer",
    "Resolver",
    "Supplier",
)

T_contra = TypeVar("T_contra", contravariant=True)
T_co = TypeVar("T_co", covariant=True)
R_co = TypeVar("R_co", covariant=True)


class CallNext(Protocol):
    def __call__(self, request: Request, /) -> Response:
        ...


class Supplier(Protocol[T_co]):
    def __call__(self) -> T_co:
        ...


class Resolver(Protocol[T_co]):
    def __call__(self, response: Response, /) -> T_co:
        ...


class Composer(Protocol):
    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        ...


class RequestConsumer(Protocol):
    def __call__(self, request: RequestOptions, /) -> None:
        ...
