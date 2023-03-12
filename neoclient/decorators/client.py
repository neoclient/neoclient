from typing import Sequence

from .api import Decorator, CompositionDecorator
from ..consumers import BaseURLConsumer, VerifyConsumer
from ..types import VerifyTypes


__all__: Sequence[str] = (
    "base_url",
    "verify",
)


def base_url(base_url: str, /) -> Decorator:
    return CompositionDecorator(BaseURLConsumer(base_url))


def verify(verify: VerifyTypes, /) -> Decorator:
    return CompositionDecorator(VerifyConsumer(verify))
