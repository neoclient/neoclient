from typing import Callable, Sequence, Type, TypeVar

from mediate.protocols import MiddlewareCallable

from ..consumers import (
    CookieConsumer,
    CookiesConsumer,
    HeaderConsumer,
    HeadersConsumer,
    QueriesConsumer,
    QueryConsumer,
    TimeoutConsumer,
    VerifyConsumer,
)
from ..enums import HTTPHeader
from ..errors import CompositionError
from ..models import Request, Response
from ..operation import Operation, get_operation
from ..service import ClientSpecification, Service
from ..types import (
    CookiesTypes,
    CookieTypes,
    HeadersTypes,
    HeaderTypes,
    QueriesTypes,
    QueryTypes,
    TimeoutTypes,
    VerifyTypes,
)
from ..typing import Dependency
from .api import ConsumerDecorator

__all__: Sequence[str] = (
    "accept",
    "cookie",
    "cookies",
    "request_depends",
    "response_depends",
    "header",
    "headers",
    "middleware",
    "query",
    "query_params",
    "referer",
    "timeout",
    "user_agent",
    "verify",
)

TT = TypeVar("TT", Callable, Type[Service])


def accept(*content_types: str) -> Callable[[TT], TT]:
    return ConsumerDecorator(
        HeaderConsumer(
            HTTPHeader.ACCEPT,
            ",".join(content_types),
        )
    )


def request_depends(*dependencies: Dependency) -> Callable[[TT], TT]:
    def decorate(target: TT, /) -> TT:
        if isinstance(target, type):
            if not issubclass(target, Service):
                raise CompositionError(f"Target class is not a subclass of {Service}")

            client_specification: ClientSpecification = target._spec

            client_specification.request_dependencies.extend(dependencies)
        elif callable(target):
            operation: Operation = get_operation(target)

            operation.request_dependencies.extend(dependencies)
        else:
            raise CompositionError(f"Target of unsupported type {type(target)}")

        return target

    return decorate


def response_depends(*dependencies: Dependency) -> Callable[[TT], TT]:
    def decorate(target: TT, /) -> TT:
        if isinstance(target, type):
            if not issubclass(target, Service):
                raise CompositionError(f"Target class is not a subclass of {Service}")

            client_specification: ClientSpecification = target._spec

            client_specification.response_dependencies.extend(dependencies)
        elif callable(target):
            operation: Operation = get_operation(target)

            operation.response_dependencies.extend(dependencies)
        else:
            raise CompositionError(f"Target of unsupported type {type(target)}")

        return target

    return decorate


def cookie(key: str, value: CookieTypes) -> Callable[[TT], TT]:
    return ConsumerDecorator(CookieConsumer(key, value))


def cookies(cookies: CookiesTypes, /) -> Callable[[TT], TT]:
    return ConsumerDecorator(CookiesConsumer(cookies))


def header(key: str, value: HeaderTypes) -> Callable[[TT], TT]:
    return ConsumerDecorator(HeaderConsumer(key, value))


def headers(headers: HeadersTypes, /) -> Callable[[TT], TT]:
    return ConsumerDecorator(HeadersConsumer(headers))


def middleware(*middleware: MiddlewareCallable[Request, Response]) -> Callable[[TT], TT]:
    def decorate(target: TT, /) -> TT:
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


def query(key: str, value: QueryTypes) -> Callable[[TT], TT]:
    return ConsumerDecorator(QueryConsumer(key, value))


def query_params(params: QueriesTypes, /) -> Callable[[TT], TT]:
    return ConsumerDecorator(QueriesConsumer(params))


def referer(referer: str, /) -> Callable[[TT], TT]:
    return ConsumerDecorator(
        HeaderConsumer(
            HTTPHeader.REFERER,
            referer,
        )
    )


def timeout(timeout: TimeoutTypes, /) -> Callable[[TT], TT]:
    return ConsumerDecorator(TimeoutConsumer(timeout))


def user_agent(user_agent: str, /) -> Callable[[TT], TT]:
    return ConsumerDecorator(
        HeaderConsumer(
            HTTPHeader.USER_AGENT,
            user_agent,
        )
    )


def verify(verify: VerifyTypes, /) -> Callable[[TT], TT]:
    return ConsumerDecorator(VerifyConsumer(verify))
