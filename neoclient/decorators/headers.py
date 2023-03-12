from typing import Sequence

from ..consumers import HeaderConsumer
from ..enums import HeaderName
from .api import CompositionDecorator, Decorator

__all__: Sequence[str] = (
    "accept",
    "referer",
    "user_agent",
)


def accept(*content_types: str) -> Decorator:
    return CompositionDecorator(
        HeaderConsumer(
            HeaderName.ACCEPT,
            ",".join(content_types),
        )
    )


def referer(referer: str, /) -> Decorator:
    return CompositionDecorator(
        HeaderConsumer(
            HeaderName.REFERER,
            referer,
        )
    )


def user_agent(user_agent: str, /) -> Decorator:
    return CompositionDecorator(
        HeaderConsumer(
            HeaderName.USER_AGENT,
            user_agent,
        )
    )
