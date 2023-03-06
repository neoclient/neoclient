from http import HTTPStatus

from httpx import Cookies, Headers, QueryParams

from neoclient.enums import HttpMethod
from neoclient.models import Request, Response, State
from neoclient.resolvers import (
    BodyResolver,
    CookieResolver,
    CookiesResolver,
    HeaderResolver,
    HeadersResolver,
    QueriesResolver,
    QueryResolver,
    StateResolver,
)


def test_resolver_query() -> None:
    response_with_param: Response = Response(
        HTTPStatus.OK,
        request=Request(
            HttpMethod.GET,
            "https://foo.com/?name=sam",
            params={"name": "sam"},
        ),
    )
    response_without_param: Response = Response(
        HTTPStatus.OK,
        request=Request(
            HttpMethod.GET,
            "https://foo.com/",
        ),
    )

    assert QueryResolver("name")(response_with_param) == "sam"
    assert QueryResolver("name")(response_without_param) is None


def test_resolver_header() -> None:
    response_with_header: Response = Response(
        HTTPStatus.OK,
        request=Request(HttpMethod.GET, "https://foo.com/"),
        headers={"name": "sam"},
    )
    response_without_header: Response = Response(
        HTTPStatus.OK,
        request=Request(HttpMethod.GET, "https://foo.com/"),
    )

    assert HeaderResolver("name")(response_with_header) == "sam"
    assert HeaderResolver("name")(response_without_header) is None


def test_resolver_cookie() -> None:
    response_with_cookie: Response = Response(
        HTTPStatus.OK,
        request=Request(HttpMethod.GET, "https://foo.com/"),
        headers={"Set-Cookie": "name=sam; Path=/"},
    )
    response_without_cookie: Response = Response(
        HTTPStatus.OK,
        request=Request(HttpMethod.GET, "https://foo.com/"),
    )

    assert CookieResolver("name")(response_with_cookie) == "sam"
    assert CookieResolver("name")(response_without_cookie) is None


def test_resolver_queries() -> None:
    response: Response = Response(
        HTTPStatus.OK,
        request=Request(
            HttpMethod.GET,
            "https://foo.com/",
            params={"name": "sam"},
        ),
    )

    assert QueriesResolver()(response) == QueryParams({"name": "sam"})


def test_resolver_headers() -> None:
    response: Response = Response(
        HTTPStatus.OK,
        request=Request(HttpMethod.GET, "https://foo.com/"),
        headers={"name": "sam"},
    )

    assert HeadersResolver()(response) == Headers({"name": "sam"})


def test_resolver_cookies() -> None:
    response: Response = Response(
        HTTPStatus.OK,
        request=Request(HttpMethod.GET, "https://foo.com/"),
        headers={"Set-Cookie": "name=sam; Path=/"},
    )

    assert CookiesResolver()(response) == Cookies({"name": "sam"})


def test_resolver_body() -> None:
    response: Response = Response(
        HTTPStatus.OK,
        request=Request(HttpMethod.GET, "https://foo.com/"),
        json={"name": "sam"},
    )

    assert BodyResolver()(response) == {"name": "sam"}


def test_resolver_state() -> None:
    message: str = "Hello, World!"

    response: Response = Response(
        HTTPStatus.OK,
        request=Request(HttpMethod.GET, "https://foo.com/"),
        state=State({"message": message}),
    )

    assert StateResolver("message")(response) == message
