from typing import Callable, Sequence, Type, Union
from typing_extensions import TypeAlias

from ..consumers import HeaderConsumer
from ..enums import HeaderName
from ..service import Service
from .api import ConsumerDecorator, Decorator

__all__: Sequence[str] = (
    "accept",
    "referer",
    "user_agent",
)

CommonDecorator: TypeAlias = Decorator[Union[Callable, Type[Service]]]


def accept(*content_types: str) -> CommonDecorator:
    return ConsumerDecorator(
        HeaderConsumer(
            HeaderName.ACCEPT,
            ",".join(content_types),
        )
    )


def referer(referer: str, /) -> CommonDecorator:
    return ConsumerDecorator(
        HeaderConsumer(
            HeaderName.REFERER,
            referer,
        )
    )


def user_agent(user_agent: str, /) -> CommonDecorator:
    return ConsumerDecorator(
        HeaderConsumer(
            HeaderName.USER_AGENT,
            user_agent,
        )
    )
