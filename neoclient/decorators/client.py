from typing import Sequence, Type

from typing_extensions import TypeAlias

from ..consumers import BaseURLConsumer, VerifyConsumer
from ..service import Service
from ..types import VerifyTypes
from .api import ConsumerDecorator, Decorator

__all__: Sequence[str] = (
    "base_url",
    "verify",
)

ClientDecorator: TypeAlias = Decorator[Type[Service]]


def base_url(base_url: str, /) -> ClientDecorator:
    return ConsumerDecorator(BaseURLConsumer(base_url))


def verify(verify: VerifyTypes, /) -> ClientDecorator:
    return ConsumerDecorator(VerifyConsumer(verify))
