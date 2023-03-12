from typing import Sequence

from ..consumers import BaseURLConsumer, VerifyConsumer
from ..types import VerifyTypes
from .api import CompositionDecorator, Decorator

__all__: Sequence[str] = (
    "base_url",
    "verify",
)


def base_url(base_url: str, /) -> Decorator:
    return CompositionDecorator(BaseURLConsumer(base_url))


def verify(verify: VerifyTypes, /) -> Decorator:
    return CompositionDecorator(VerifyConsumer(verify))
