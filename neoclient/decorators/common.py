from typing import Sequence

from ..consumers import (
    CookieConsumer,
    CookiesConsumer,
    FollowRedirectsConsumer,
    HeaderConsumer,
    HeadersConsumer,
    QueryConsumer,
    QueryParamsConsumer,
    TimeoutConsumer,
    VerifyConsumer,
)
from ..enums import HTTPHeader
from ..errors import CompositionError
from ..operation import Operation, get_operation
from ..services import ClientSpecification, Service
from ..types import (
    CookiesTypes,
    CookieTypes,
    HeadersTypes,
    HeaderTypes,
    QueryParamsTypes,
    QueryTypes,
    TimeoutTypes,
    VerifyTypes,
)
from ..typing import Dependency
from .api import CS, CommonDecorator, ConsumerDecorator, RequestDependsDecorator

__all__: Sequence[str] = (
    "accept",
    "cookie",
    "cookies",
    "request_depends",
    "response_depends",
    "header",
    "headers",
    "query",
    "query_params",
    "referer",
    "timeout",
    "user_agent",
    "verify",
)


def request_depends(*dependencies: Dependency) -> CommonDecorator:
    return RequestDependsDecorator(*dependencies)


def accept(*content_types: str) -> CommonDecorator:
    return ConsumerDecorator(
        HeaderConsumer(
            HTTPHeader.ACCEPT,
            ",".join(content_types),
        )
    )


def response_depends(*dependencies: Dependency) -> CommonDecorator:
    def decorate(target: CS, /) -> CS:
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


def cookie(key: str, value: CookieTypes) -> CommonDecorator:
    return ConsumerDecorator(CookieConsumer(key, value))


def cookies(cookies: CookiesTypes, /) -> CommonDecorator:
    return ConsumerDecorator(CookiesConsumer(cookies))


def header(key: str, value: HeaderTypes) -> CommonDecorator:
    return ConsumerDecorator(HeaderConsumer(key, value))


def headers(headers: HeadersTypes, /) -> CommonDecorator:
    return ConsumerDecorator(HeadersConsumer(headers))


def query(key: str, value: QueryTypes) -> CommonDecorator:
    return ConsumerDecorator(QueryConsumer(key, value))


def query_params(params: QueryParamsTypes, /) -> CommonDecorator:
    return ConsumerDecorator(QueryParamsConsumer(params))


def referer(referer: str, /) -> CommonDecorator:
    return ConsumerDecorator(
        HeaderConsumer(
            HTTPHeader.REFERER,
            referer,
        )
    )


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


def follow_redirects(follow_redirects: bool, /) -> CommonDecorator:
    return ConsumerDecorator(FollowRedirectsConsumer(follow_redirects))
