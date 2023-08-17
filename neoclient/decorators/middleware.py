from typing import Optional, Sequence

from mediate.protocols import MiddlewareCallable

from ..errors import CompositionError
from ..middlewares import (
    ExpectedContentTypeMiddleware,
    ExpectedHeaderMiddleware,
    ExpectedStatusCodeMiddleware,
)
from ..middlewares import raise_for_status as raise_for_status_middleware
from ..models import Request, Response
from ..operation import Operation, get_operation
from ..services import Service
from ..specification import ClientSpecification
from .api import CommonDecorator, CS

__all__: Sequence[str] = (
    "middleware",
    "expect_content_type",
    "expect_header",
    "expect_status",
    "raise_for_status",
)


def middleware(
    *middleware: MiddlewareCallable[Request, Response]
) -> CommonDecorator:
    def decorate(target: CS, /) -> CS:
        if isinstance(target, type):
            if not issubclass(target, Service):
                raise CompositionError(f"Target class is not a subclass of {Service}")

            client_specification: ClientSpecification = target._spec

            client_specification.middleware.add_all(middleware)
        elif callable(target):
            operation: Operation = get_operation(target)

            operation.middleware.add_all(middleware)
        else:
            raise CompositionError(f"Target of unsupported type {type(target)}")

        return target

    return decorate


def expect_content_type(content_type: str, /) -> CommonDecorator:
    return middleware(ExpectedContentTypeMiddleware(content_type))


def expect_header(name: str, value: Optional[str] = None) -> CommonDecorator:
    return middleware(ExpectedHeaderMiddleware(name, value))


def expect_status(*status_codes: int) -> CommonDecorator:
    return middleware(ExpectedStatusCodeMiddleware(*status_codes))


def raise_for_status(target: CS, /) -> CS:
    return middleware(raise_for_status_middleware)(target)
