from typing import Sequence

from mediate.protocols import MiddlewareCallable

from ..consumers import (
    CookieConsumer,
    CookiesConsumer,
    HeaderConsumer,
    HeadersConsumer,
    QueriesConsumer,
    QueryConsumer,
    TimeoutConsumer,
)
from ..errors import CompositionError
from ..models import Request, Response
from ..operation import OperationSpecification, get_operation
from ..service import ClientSpecification, Service
from ..types import (
    CookiesTypes,
    CookieTypes,
    HeadersTypes,
    HeaderTypes,
    QueriesTypes,
    QueryTypes,
    TimeoutTypes,
)
from .api import CompositionDecorator, Decorator, T

__all__: Sequence[str] = (
    "cookie",
    "cookies",
    "header",
    "headers",
    "middleware",
    "query",
    "query_params",
    "timeout",
)


def cookie(key: str, value: CookieTypes) -> Decorator:
    return CompositionDecorator(CookieConsumer(key, value))


def cookies(cookies: CookiesTypes, /) -> Decorator:
    return CompositionDecorator(CookiesConsumer(cookies))


def header(key: str, value: HeaderTypes) -> Decorator:
    return CompositionDecorator(HeaderConsumer(key, value))


def headers(headers: HeadersTypes, /) -> Decorator:
    return CompositionDecorator(HeadersConsumer(headers))


def middleware(*middleware: MiddlewareCallable[Request, Response]) -> Decorator:
    def decorate(target: T, /) -> T:
        if isinstance(target, type):
            if not issubclass(target, Service):
                raise CompositionError(f"Target class is not a subclass of {Service}")

            client_specification: ClientSpecification = target._spec

            client_specification.middleware.add_all(middleware)
        elif callable(target):
            operation_specification: OperationSpecification = get_operation(
                target
            ).specification

            operation_specification.middleware.add_all(middleware)
        else:
            raise CompositionError(f"Target of unsupported type {type(target)}")

        return target

    return decorate


def query(key: str, value: QueryTypes) -> Decorator:
    return CompositionDecorator(QueryConsumer(key, value))


def query_params(params: QueriesTypes, /) -> Decorator:
    return CompositionDecorator(QueriesConsumer(params))


def timeout(timeout: TimeoutTypes, /) -> Decorator:
    return CompositionDecorator(TimeoutConsumer(timeout))
