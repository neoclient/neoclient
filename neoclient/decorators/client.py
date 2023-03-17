from typing import Sequence, Type

from typing_extensions import TypeAlias

from ..consumers import BaseURLConsumer
from ..service import Service
from .api import ConsumerDecorator, Decorator

__all__: Sequence[str] = ("base_url",)

ClientDecorator: TypeAlias = Decorator[Type[Service]]


def base_url(base_url: str, /) -> ClientDecorator:
    return ConsumerDecorator(BaseURLConsumer(base_url))
