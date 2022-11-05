from typing import List, Protocol, TypeVar, runtime_checkable

from httpx import Response

T = TypeVar("T", covariant=True)

__all__: List[str] = [
    "ResolutionFunction",
]


@runtime_checkable
class ResolutionFunction(Protocol[T]):
    def __call__(self, response: Response, /) -> T:
        ...
