from typing import Any, Optional

from httpx import Response
from loguru import logger

from ..errors import ResolutionError
from ..parameters import BaseParameter
from .resolvers import Resolver, resolvers
from .typing import ResolutionFunction


def resolve(
    response: Response,
    parameter: BaseParameter,
) -> Any:
    logger.info(f"Resolving parameter {parameter!r} for response {response!r}")

    print("Resolvers:", resolvers)

    resolver: Optional[Resolver] = resolvers.get(type(parameter))

    if resolver is None:
        raise ResolutionError(f"Failed to find resolver for parameter {parameter!r}")

    logger.info(f"Found resolver: {resolver!r}")

    resolution_function: ResolutionFunction = resolver(parameter)

    logger.info(f"Applying resolution function: {resolver!r} to response {response!r}")

    return resolution_function(response)
