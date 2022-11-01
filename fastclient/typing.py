# from typing import Any, Protocol, TypeVar, runtime_checkable
from typing import Protocol, TypeVar

# from httpx import Response

# from .models import RequestOptions

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


# @runtime_checkable
# class Resolvable(Protocol[T_co]):
#     def resolve(self, response: Response, /) -> T_co:
#         ...


# @runtime_checkable
# class Composable(Protocol):
#     def compose(self, request: RequestOptions, argument: Any, /) -> None:
#         ...
