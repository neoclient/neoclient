from typing import Any, MutableSequence

from httpx import Cookies, Headers, QueryParams

from neoclient import converters, utils
from neoclient.decorators.api import (
    Options,
    client_options_decorator,
    cookies_decorator,
    headers_decorator,
    options_decorator,
    params_decorator,
    request_dependencies_decorator,
    response_dependencies_decorator,
)
from neoclient.models import ClientOptions

from ..types import (
    CookiesTypes,
    HeadersTypes,
    QueryParamsTypes,
    TimeoutTypes,
    VerifyTypes,
)
from ..typing import Dependency

__all__ = (
    "request_depends",
    "response_depends",
    "cookie",
    "set_cookies",
    "update_cookies",
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
    "set_params",
    "add_params",
    "merge_params",
    "params",
    "timeout",
    "verify",
    "follow_redirects",
)


# TODO: Type responses


def request_depends(*dependencies: Dependency):
    @request_dependencies_decorator
    def decorate(request_dependencies: MutableSequence[Dependency], /) -> None:
        request_dependencies.extend(dependencies)

    return decorate


def response_depends(*dependencies: Dependency):
    @response_dependencies_decorator
    def decorate(response_dependencies: MutableSequence[Dependency], /) -> None:
        response_dependencies.extend(dependencies)

    return decorate


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


def cookies(cookies: CookiesTypes, /):
    return update_cookies(cookies)


# WARN: Currently only accepts a `str` value - should accept `HeaderTypes`?
def set_header(key: str, value: str, /):
    """Set the header `key` to `value`, removing any duplicate entries."""

    @headers_decorator
    def decorate(headers: Headers, /) -> None:
        headers[key] = value

    return decorate


def add_header(key: str, value: str, /):
    """Add the header `key` with value `value`, keeping any duplicate entries."""

    @headers_decorator
    def decorate(headers: Headers, /) -> None:
        utils.add_header(headers, key, value)

    return decorate


def header(key: str, value: str, /):
    return add_header(key, value)


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


def headers(headers: HeadersTypes, /):
    return add_headers(headers)


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


def param(key: str, value: Any = None):
    return add_param(key, value)


def set_params(params: QueryParamsTypes, /):
    @options_decorator
    def decorate(options: Options, /) -> None:
        options.params = converters.convert_query_params(params)

    return decorate


def add_params(params: QueryParamsTypes, /):
    @options_decorator
    def decorate(options: Options, /) -> None:
        options.params = utils.add_params(
            options.params, converters.convert_query_params(params)
        )

    return decorate


# Note: Should this instead use "update" terminology?
def merge_params(params: QueryParamsTypes, /):
    @options_decorator
    def decorate(options: Options, /) -> None:
        options.params = options.params.merge(converters.convert_query_params(params))

    return decorate


def params(params: QueryParamsTypes, /):
    return add_params(params)


def timeout(timeout: TimeoutTypes, /):
    @options_decorator
    def decorate(options: Options, /) -> None:
        options.timeout = converters.convert_timeout(timeout)

    return decorate


# Note: Does this decorator belong here?
# It's common in that it can be applied to a ClientSpecification or Operation.
# But it's not common in that it can only be applied to ClientOptions.
def verify(verify: VerifyTypes, /):
    @client_options_decorator
    def decorate(client_options: ClientOptions, /) -> None:
        client_options.verify = verify

    return decorate


def follow_redirects(follow_redirects: bool, /):
    @options_decorator
    def decorate(options: Options, /) -> None:
        options.follow_redirects = follow_redirects

    return decorate
