from typing import Callable, Sequence, Type, TypeVar

from ..consumers import BaseURLConsumer
from ..services import Service
from .api import ConsumerDecorator

__all__: Sequence[str] = ("base_url",)

TT = TypeVar("TT", Callable, Type[Service])


def base_url(base_url: str, /) -> Callable[[TT], TT]:
    return ConsumerDecorator(BaseURLConsumer(base_url))
