from typing import Any, List, Protocol, TypeVar

from httpx import Response

from .models import RequestOptions

__all__: List[str] = [
    "Supplier",
    "Consumer",
    "Function",
    "Resolver",
    "Composer"
]

T_contra = TypeVar("T_contra", contravariant=True)
T_co = TypeVar("T_co", covariant=True)
R_co = TypeVar("R_co", covariant=True)


class Supplier(Protocol[T_co]):
    def __call__(self) -> T_co:
        ...


class Consumer(Protocol[T_contra]):
    def __call__(self, value: T_contra, /) -> None:
        ...


class Function(Protocol[T_contra, R_co]):
    def __call__(self, value: T_contra, /) -> R_co:
        ...


class Resolver(Protocol[T_co]):
    def __call__(self, response: Response, /) -> T_co:
        ...


class Composer(Protocol):
    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        ...
