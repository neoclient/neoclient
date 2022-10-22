from typing import Callable, Protocol, TypeVar

from ..models import RequestOptions

C = TypeVar("C", bound=Callable)


class Decorator(Protocol):
    def __call__(self, func: C, /) -> C:
        ...


class Composer(Protocol):
    def __call__(self, request: RequestOptions, /) -> None:
        ...