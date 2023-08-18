from dataclasses import dataclass
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
from .api import (
    CommonDecorator,
    ConsumerDecorator,
    SupportsConsumeClientSpecification,
    SupportsConsumeOperation,
)

__all__: Sequence[str] = (
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
class RequestDependsConsumer(
    SupportsConsumeClientSpecification, SupportsConsumeOperation
):
    dependencies: Sequence[Dependency]

    def consume_client_spec(self, client_specification: ClientSpecification) -> None:
        client_specification.request_dependencies.extend(self.dependencies)

    def consume_operation(self, operation: Operation) -> None:
        operation.request_dependencies.extend(self.dependencies)


@dataclass
class ResponseDependsConsumer(
    SupportsConsumeClientSpecification, SupportsConsumeOperation
):
    dependencies: Sequence[Dependency]

    def consume_client_spec(self, client_specification: ClientSpecification) -> None:
        client_specification.response_dependencies.extend(self.dependencies)

    def consume_operation(self, operation: Operation) -> None:
        operation.response_dependencies.extend(self.dependencies)


def request_depends(*dependencies: Dependency) -> CommonDecorator:
    return ConsumerDecorator(RequestDependsConsumer(dependencies))


def response_depends(*dependencies: Dependency) -> CommonDecorator:
    return ConsumerDecorator(ResponseDependsConsumer(dependencies))


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


def timeout(timeout: TimeoutTypes, /) -> CommonDecorator:
    return ConsumerDecorator(TimeoutConsumer(timeout))


def verify(verify: VerifyTypes, /) -> CommonDecorator:
    return ConsumerDecorator(VerifyConsumer(verify))


def follow_redirects(follow_redirects: bool, /) -> CommonDecorator:
    return ConsumerDecorator(FollowRedirectsConsumer(follow_redirects))
