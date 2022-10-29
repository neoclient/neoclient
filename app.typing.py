from typing import Protocol, TypeVar

from fastclient.types import HeaderTypes

T = TypeVar("T", contravariant=True, bound=HeaderTypes)


class Foo(Protocol[T]):
    def bar(self, value: T, /) -> None:
        ...
