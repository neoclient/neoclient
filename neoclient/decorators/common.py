from dataclasses import dataclass
from typing import MutableSequence, Sequence

from neoclient.decorators.api import Decorator

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
from ..operation import Operation
from ..services import ClientSpecification
from ..specification import ClientSpecification
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
from .old_api import ConsumerDecorator

__all__ = (
    "cookie",
    "cookies",
    "request_depends",
    "response_depends",
    "header",
    "headers",
    "query",
    "query_params",
    "timeout",
    "verify",
)


@dataclass
class RequestDependsDecorator(Decorator):
    dependencies: Sequence[Dependency]

    def decorate_operation(self, operation: Operation, /) -> None:
        return self.consumer(operation.request_dependencies)

    def decorate_client(self, client: ClientSpecification, /) -> None:
        return self.consumer(client.request_dependencies)

    def _decorate_request_dependencies(
        self, request_dependencies: MutableSequence[Dependency], /
    ) -> None:
        request_dependencies.extend(self.dependencies)


@dataclass
class ResponseDependsDecorator(Decorator):
    dependencies: Sequence[Dependency]

    def decorate_operation(self, operation: Operation, /) -> None:
        return self.consumer(operation.response_dependencies)

    def decorate_client(self, client: ClientSpecification, /) -> None:
        return self.consumer(client.response_dependencies)

    def _decorate_response_dependencies(
        self, response_dependencies: MutableSequence[Dependency], /
    ) -> None:
        response_dependencies.extend(self.dependencies)


# TODO: Type responses


def request_depends(*dependencies: Dependency):
    return RequestDependsDecorator(dependencies)


def response_depends(*dependencies: Dependency):
    return ResponseDependsDecorator(dependencies)


def cookie(key: str, value: CookieTypes):
    return ConsumerDecorator(CookieConsumer(key, value))


def cookies(cookies: CookiesTypes, /):
    return ConsumerDecorator(CookiesConsumer(cookies))


def header(key: str, value: HeaderTypes):
    return ConsumerDecorator(HeaderConsumer(key, value))


def headers(headers: HeadersTypes, /):
    return ConsumerDecorator(HeadersConsumer(headers))


def query(key: str, value: QueryTypes):
    return ConsumerDecorator(QueryConsumer(key, value))


def query_params(params: QueryParamsTypes, /):
    return ConsumerDecorator(QueryParamsConsumer(params))


def timeout(timeout: TimeoutTypes, /):
    return ConsumerDecorator(TimeoutConsumer(timeout))


def verify(verify: VerifyTypes, /):
    return ConsumerDecorator(VerifyConsumer(verify))


def follow_redirects(follow_redirects: bool, /):
    return ConsumerDecorator(FollowRedirectsConsumer(follow_redirects))
