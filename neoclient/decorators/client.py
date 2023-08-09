from typing import Callable, Sequence, Type, TypeVar

from ..consumers import BaseURLConsumer
from ..service import Service
from .api import ConsumerDecorator

__all__: Sequence[str] = ("base_url",)

TT = TypeVar("TT", Callable, Type[Service])

Foo = Callable[[TT], TT]


def base_url(base_url: str, /):
    return ConsumerDecorator(BaseURLConsumer(base_url))
