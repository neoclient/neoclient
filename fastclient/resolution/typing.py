from typing import Protocol, TypeVar, runtime_checkable

from httpx import Response

T = TypeVar("T", covariant=True)


@runtime_checkable
class ResolutionFunction(Protocol[T]):
    def __call__(self, response: Response, /) -> T:
        ...
