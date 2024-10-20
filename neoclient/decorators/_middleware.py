from typing import Optional

from mediate.protocols import MiddlewareCallable

from neoclient.decorators.api import CS, middleware_decorator
from neoclient.middleware import (
    ExpectedContentTypeMiddleware,
    ExpectedHeaderMiddleware,
    ExpectedStatusCodeMiddleware,
    Middleware,
)
from neoclient.middleware import raise_for_status as raise_for_status_middleware
from neoclient.models import Request, Response

__all__ = (
    "middleware",
    "expect_content_type",
    "expect_header",
    "expect_status",
    "raise_for_status",
)

# TODO: Type responses


def middleware(*middlewares: MiddlewareCallable[Request, Response]):
    @middleware_decorator
    def decorate(middleware: Middleware, /) -> None:
        middleware.add_all(middlewares)

    return decorate


def expect_content_type(content_type: str, /):
    return middleware(ExpectedContentTypeMiddleware(content_type))


def expect_header(name: str, value: Optional[str] = None):
    return middleware(ExpectedHeaderMiddleware(name, value))


def expect_status(*status_codes: int):
    return middleware(ExpectedStatusCodeMiddleware(*status_codes))


def raise_for_status(target: CS, /) -> CS:
    return middleware(raise_for_status_middleware)(target)
