from typing import Callable, Sequence, Type, Union

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
from ..enums import HeaderName
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
    VerifyTypes,
)
from .api import ConsumerDecorator, Decorator, T

__all__: Sequence[str] = (
    "accept",
    "cookie",
    "cookies",
    "header",
    "headers",
    "middleware",
    "query",
    "query_params",
    "referer",
    "timeout",
    "user_agent",
)

CommonDecorator: TypeAlias = Decorator[Union[Callable, Type[Service]]]


def accept(*content_types: str) -> CommonDecorator:
    return ConsumerDecorator(
        HeaderConsumer(
            HeaderName.ACCEPT,
            ",".join(content_types),
        )
    )


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
            operation_specification: OperationSpecification = get_operation(
                target
            ).request_options

            operation_specification.middleware.add_all(middleware)
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
            HeaderName.REFERER,
            referer,
        )
    )


def timeout(timeout: TimeoutTypes, /) -> CommonDecorator:
    return ConsumerDecorator(TimeoutConsumer(timeout))


def user_agent(user_agent: str, /) -> CommonDecorator:
    return ConsumerDecorator(
        HeaderConsumer(
            HeaderName.USER_AGENT,
            user_agent,
        )
    )


def verify(verify: VerifyTypes, /) -> CommonDecorator:
    return ConsumerDecorator(VerifyConsumer(verify))
