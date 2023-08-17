from dataclasses import dataclass
from typing import Optional, Sequence

from mediate.protocols import MiddlewareCallable

from ..middlewares import (
    ExpectedContentTypeMiddleware,
    ExpectedHeaderMiddleware,
    ExpectedStatusCodeMiddleware,
)
from ..middlewares import raise_for_status as raise_for_status_middleware
from ..models import Request, Response
from ..operation import Operation
from ..specification import ClientSpecification
from .api import (
    CS,
    CommonDecorator,
    ConsumerDecorator,
    SupportsConsumeClientSpecification,
    SupportsConsumeOperation,
)

__all__: Sequence[str] = (
    "middleware",
    "expect_content_type",
    "expect_header",
    "expect_status",
    "raise_for_status",
)


@dataclass
class MiddlewareConsumer(SupportsConsumeClientSpecification, SupportsConsumeOperation):
    middleware: Sequence[MiddlewareCallable[Request, Response]]

    def consume_client_spec(self, client_specification: ClientSpecification) -> None:
        client_specification.middleware.add_all(self.middleware)

    def consume_operation(self, operation: Operation) -> None:
        operation.middleware.add_all(self.middleware)


def middleware(*middleware: MiddlewareCallable[Request, Response]) -> CommonDecorator:
    return ConsumerDecorator(MiddlewareConsumer(middleware))


def expect_content_type(content_type: str, /) -> CommonDecorator:
    return middleware(ExpectedContentTypeMiddleware(content_type))


def expect_header(name: str, value: Optional[str] = None) -> CommonDecorator:
    return middleware(ExpectedHeaderMiddleware(name, value))


def expect_status(*status_codes: int) -> CommonDecorator:
    return middleware(ExpectedStatusCodeMiddleware(*status_codes))


def raise_for_status(target: CS, /) -> CS:
    return middleware(raise_for_status_middleware)(target)
