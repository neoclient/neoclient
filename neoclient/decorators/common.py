from dataclasses import dataclass
from typing import MutableSequence, Sequence, Tuple

from httpx import Headers

from neoclient import converters, utils
from neoclient.decorators.api import (
    Decorator,
    request_options_decorator,
)
from neoclient.models import RequestOptions

from ..consumers import (
    CookieConsumer,
    CookiesConsumer,
    FollowRedirectsConsumer,
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


def header(key: str, value: HeaderTypes, /, *, keep_existing: bool = False):
    @request_options_decorator
    def decorate(request_options: RequestOptions, /) -> None:
        values: Sequence[str] = converters.convert_header(value)

        headers_old: Headers = request_options.headers
        headers_new: Headers = Headers([(key, value) for value in values])

        if not keep_existing and key in headers_old:
            del headers_old[key]

        request_options.headers = utils.merge_headers(headers_old, headers_new)

    return decorate


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
