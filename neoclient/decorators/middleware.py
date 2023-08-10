from typing import Any, Callable, Optional, Sequence, Type, TypeVar

from ..middleware import (
    ExpectedContentTypeMiddleware,
    ExpectedHeaderMiddleware,
    ExpectedStatusCodeMiddleware,
)
from ..middleware import raise_for_status as raise_for_status_middleware
from ..service import Service
from .common import middleware as middleware_decorator

__all__: Sequence[str] = (
    "expect_content_type",
    "expect_header",
    "expect_status",
    "raise_for_status",
)

C = TypeVar("C", bound=Callable[..., Any])
S = TypeVar("S", bound=Type[Service])
CS = TypeVar("CS", Callable[..., Any], Type[Service])


def expect_content_type(content_type: str, /) -> Callable[[CS], CS]:
    return middleware_decorator(ExpectedContentTypeMiddleware(content_type))


def expect_header(name: str, value: Optional[str] = None) -> Callable[[CS], CS]:
    return middleware_decorator(ExpectedHeaderMiddleware(name, value))


def expect_status(*status_codes: int) -> Callable[[CS], CS]:
    return middleware_decorator(ExpectedStatusCodeMiddleware(*status_codes))


def raise_for_status(target: CS, /) -> CS:
    return middleware_decorator(raise_for_status_middleware)(target)
