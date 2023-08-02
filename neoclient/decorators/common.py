from typing import Any, Callable, Sequence, Type, Union

from mediate.protocols import MiddlewareCallable
from typing_extensions import TypeAlias

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
from .api import ConsumerDecorator, Decorator, T

__all__: Sequence[str] = (
    "accept",
    "cookie",
    "cookies",
    "depends",
    "header",
    "headers",
    "middleware",
    "query",
    "query_params",
    "referer",
    "response",
    "timeout",
    "user_agent",
    "verify",
)

CommonDecorator: TypeAlias = Decorator[Union[Callable, Type[Service]]]


def accept(*content_types: str) -> CommonDecorator:
    return ConsumerDecorator(
        HeaderConsumer(
            HTTPHeader.ACCEPT,
            ",".join(content_types),
        )
    )


def depends(*dependencies: Callable[..., Any]) -> CommonDecorator:
    def decorate(target: T, /) -> T:
        if isinstance(target, type):
            if not issubclass(target, Service):
                raise CompositionError(f"Target class is not a subclass of {Service}")

            client_specification: ClientSpecification = target._spec

            client_specification.dependencies.extend(dependencies)
        elif callable(target):
            operation: Operation = get_operation(target)

            operation.dependencies.extend(dependencies)
        else:
            raise CompositionError(f"Target of unsupported type {type(target)}")

        return target

    return decorate


def cookie(key: str, value: CookieTypes) -> CommonDecorator:
    return ConsumerDecorator(CookieConsumer(key, value))


def cookies(cookies: CookiesTypes, /) -> CommonDecorator:
    return ConsumerDecorator(CookiesConsumer(cookies))


def header(key: str, value: HeaderTypes) -> CommonDecorator:
    return ConsumerDecorator(HeaderConsumer(key, value))


def headers(headers: HeadersTypes, /) -> CommonDecorator:
    return ConsumerDecorator(HeadersConsumer(headers))


def middleware(*middleware: MiddlewareCallable[Request, Response]) -> CommonDecorator:
    def decorate(target: T, /) -> T:
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


def query(key: str, value: QueryTypes) -> CommonDecorator:
    return ConsumerDecorator(QueryConsumer(key, value))


def query_params(params: QueriesTypes, /) -> CommonDecorator:
    return ConsumerDecorator(QueriesConsumer(params))


def referer(referer: str, /) -> CommonDecorator:
    return ConsumerDecorator(
        HeaderConsumer(
            HTTPHeader.REFERER,
            referer,
        )
    )


def response(response: Callable[..., Any]) -> CommonDecorator:
    def decorate(target: T, /) -> T:
        if isinstance(target, type):
            if not issubclass(target, Service):
                raise CompositionError(f"Target class is not a subclass of {Service}")

            client_specification: ClientSpecification = target._spec

            client_specification.default_response = response
        elif callable(target):
            operation: Operation = get_operation(target)

            operation.response = response
        else:
            raise CompositionError(f"Target of unsupported type {type(target)}")

        return target

    return decorate


def timeout(timeout: TimeoutTypes, /) -> CommonDecorator:
    return ConsumerDecorator(TimeoutConsumer(timeout))


def user_agent(user_agent: str, /) -> CommonDecorator:
    return ConsumerDecorator(
        HeaderConsumer(
            HTTPHeader.USER_AGENT,
            user_agent,
        )
    )


def verify(verify: VerifyTypes, /) -> CommonDecorator:
    return ConsumerDecorator(VerifyConsumer(verify))
