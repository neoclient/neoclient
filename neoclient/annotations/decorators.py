from typing import Callable, Sequence, TypeVar

from mediate.protocols import MiddlewareCallable, MiddlewareMethod

from ..models import Request, Response
from .api import add_annotation
from .enums import Annotation

__all__: Sequence[str] = (
    "service_middleware",
    "service_response",
)

C = TypeVar("C", bound=Callable)
M = TypeVar(
    "M", MiddlewareCallable[Request, Response], MiddlewareMethod[Request, Response]
)


def service_middleware(middleware: M, /) -> M:
    add_annotation(middleware, Annotation.MIDDLEWARE)

    return middleware


def service_response(response: C, /) -> C:
    add_annotation(response, Annotation.RESPONSE)

    return response
