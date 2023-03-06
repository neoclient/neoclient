from typing import Sequence, TypeVar

from mediate.protocols import MiddlewareCallable, MiddlewareMethod

from ..models import Request, Response
from .api import add_annotation
from .enums import Annotation

__all__: Sequence[str] = ("service_middleware",)

M = TypeVar(
    "M", MiddlewareCallable[Request, Response], MiddlewareMethod[Request, Response]
)


def service_middleware(middleware: M, /) -> M:
    add_annotation(middleware, Annotation.MIDDLEWARE)

    return middleware