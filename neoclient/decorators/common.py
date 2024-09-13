from dataclasses import dataclass
from typing import Any, MutableSequence, Sequence

from httpx import Cookies, Headers, QueryParams

from neoclient import converters, utils
from neoclient.decorators.api import (
    Decorator,
    Options,
    cookies_decorator,
    headers_decorator,
    options_decorator,
    params_decorator,
)
from neoclient.specification import ClientSpecification

from ..consumers import (
    CookieConsumer,
    CookiesConsumer,
    FollowRedirectsConsumer,
    HeadersConsumer,
    QueryParamsConsumer,
    TimeoutConsumer,
    VerifyConsumer,
)
from ..operation import Operation
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
    "request_depends",
    "response_depends",
    "cookie",
    "cookies",
    "set_header",
    "add_header",
    "header",
    "set_headers",
    "add_headers",
    "update_headers",
    "headers",
    "set_param",
    "add_param",
    "param",
    "params",
    "timeout",
    "verify",
    "follow_redirects",
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


def cookie(name: str, value: str, domain: str = "", path: str = "/"):
    """Set a cookie value by name. May optionally include domain and path."""

    @cookies_decorator
    def decorate(cookies: Cookies, /) -> None:
        cookies.set(name, value, domain, path)

    return decorate


def set_cookies(cookies: CookiesTypes, /):
    @options_decorator
    def decorate(options: Options, /) -> None:
        options.cookies = converters.convert_cookies(cookies)

    return decorate


def update_cookies(cookies: CookiesTypes, /):
    @options_decorator
    def decorate(options: Options, /) -> None:
        options.cookies.update(converters.convert_cookies(cookies))

    return decorate


cookies = update_cookies


# WARN: Currently only accepts a `str` value - should accept `HeaderTypes`?
def set_header(key: str, value: str, /):
    """
    Set Header Decorator.

    Set the header `key` to `value`, removing any duplicate entries.
    Retains insertion order.

    Args:
        key:   The header key   (e.g. "User-Agent")
        value: The header value (e.g. "Mozilla/5.0")

    Returns:
        TODO TODO TODO

    Raises:
        TODO: TODO
    """

    @headers_decorator
    def decorate(headers: Headers, /) -> None:
        headers[key] = value

    return decorate


def add_header(key: str, value: str, /):
    """
    Add Header Decorator.

    Add the header `key` with value `value`, keeping any duplicate entries.
    Retains insertion order.

    Args:
        key:   The header key   (e.g. "User-Agent")
        value: The header value (e.g. "Mozilla/5.0")

    Returns:
        TODO TODO TODO

    Raises:
        TODO: TODO
    """

    @headers_decorator
    def decorate(headers: Headers, /) -> None:
        utils.add_header(headers, key, value)

    return decorate


# Header decorator
header = add_header


# NOTE: Should `HeadersTypes` should come as-is from `httpx`?
def set_headers(headers: HeadersTypes, /):
    @options_decorator
    def decorate(options: Options, /) -> None:
        options.headers = Headers(headers)

    return decorate


def add_headers(headers: HeadersTypes, /):
    @options_decorator
    def decorate(options: Options, /) -> None:
        utils.add_headers(options.headers, Headers(headers))

    return decorate


def update_headers(headers: HeadersTypes, /):
    @options_decorator
    def decorate(options: Options, /) -> None:
        options.headers.update(headers)

    return decorate


headers = add_headers


# WARN: should accept `QueryTypes`?
def set_param(key: str, value: Any = None):
    @params_decorator
    def decorate(params: QueryParams, /) -> QueryParams:
        return params.set(key, value)

    return decorate


def add_param(key: str, value: Any = None):
    @params_decorator
    def decorate(params: QueryParams, /) -> QueryParams:
        return params.add(key, value)

    return decorate


param = add_param


def params(params: QueryParamsTypes, /):
    return ConsumerDecorator(QueryParamsConsumer(params))


def timeout(timeout: TimeoutTypes, /):
    return ConsumerDecorator(TimeoutConsumer(timeout))


def verify(verify: VerifyTypes, /):
    return ConsumerDecorator(VerifyConsumer(verify))


def follow_redirects(follow_redirects: bool, /):
    return ConsumerDecorator(FollowRedirectsConsumer(follow_redirects))
