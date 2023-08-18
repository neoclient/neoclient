from typing import Sequence

from ..consumers import BaseURLConsumer
from .api import ServiceConsumerDecorator, ServiceDecorator

__all__: Sequence[str] = ("base_url",)


def base_url(base_url: str, /) -> ServiceDecorator:
    return ServiceConsumerDecorator(BaseURLConsumer(base_url))
