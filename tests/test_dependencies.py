from http import HTTPStatus

from httpx import Request, Response, Headers
from pydantic import Required

from neoclient import Cookie
from neoclient.params import (
    QueryParameter,
    BodyParameter,
    HeadersParameter,
    CookieParameter,
)
from neoclient.dependencies import DependencyResolver, get_fields
from neoclient.enums import HttpMethod


def test_get_fields() -> None:
    def foo(query: str, body: dict, headers: Headers, cookie: int = Cookie()) -> None:
        ...

    assert get_fields(foo) == {
        "query": (str, QueryParameter(alias="query", default=Required)),
        "body": (dict, BodyParameter(alias="body", default=Required)),
        "headers": (Headers, HeadersParameter(alias="headers", default=Required)),
        "cookie": (int, CookieParameter(alias="cookie", default=Required)),
    }


def test_DependencyResolver() -> None:
    def dependency(response: Response, /) -> Response:
        return response

    response: Response = Response(
        HTTPStatus.OK, request=Request(HttpMethod.GET, "https://foo.com/")
    )

    assert DependencyResolver(dependency)(response) == response


def test_DependencyParameter() -> None:
    ...
