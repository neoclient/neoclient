from typing import Any, Optional

import param.parameters
from loguru import logger

from .composers import composers, Composer
from .typing import RequestConsumer
from ..errors import CompositionError
from ..models import RequestOptions


def compose(
    request: RequestOptions, param: param.parameters.Param, argument: Any
) -> None:
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
