from typing import Any, Optional

from loguru import logger

from ..errors import CompositionError
from ..models import RequestOptions
from ..parameters import BaseParameter
from .composers import Composer, composers
from .typing import RequestConsumer


def compose(request: RequestOptions, param: BaseParameter, argument: Any) -> None:
    logger.debug(
        "Composing param {param!r} with argument {argument!r}",
        param=param,
        argument=argument,
    )

    composer: Optional[Composer] = composers.get(type(param))

    if composer is None:
        raise CompositionError(f"Failed to find composer for param {param!r}")

    logger.debug(f"Found composer: {composer!r}")

    consumer: RequestConsumer = composer(param, argument)

    logger.debug(f"Applying request consumer: {consumer!r}")

    consumer(request)
