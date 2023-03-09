from httpx import Cookies, Headers, QueryParams

from neoclient.models import Response, State
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

from . import utils


def test_resolver_query() -> None:
    response_with_param: Response = utils.build_response(
        request=utils.build_request(
            params={"name": "sam"},
        )
    )
    response_without_param: Response = utils.build_response()

    assert QueryResolver("name")(response_with_param) == "sam"
    assert QueryResolver("name")(response_without_param) is None


def test_resolver_header() -> None:
    response_with_header: Response = utils.build_response(
        headers={"name": "sam"},
    )
    response_without_header: Response = utils.build_response()

    assert HeaderResolver("name")(response_with_header) == "sam"
    assert HeaderResolver("name")(response_without_header) is None


def test_resolver_cookie() -> None:
    response_with_cookie: Response = utils.build_response(
        headers={"Set-Cookie": "name=sam; Path=/"},
    )
    response_without_cookie: Response = utils.build_response()

    assert CookieResolver("name")(response_with_cookie) == "sam"
    assert CookieResolver("name")(response_without_cookie) is None


def test_resolver_queries() -> None:
    response: Response = utils.build_response(
        request=utils.build_request(
            params={"name": "sam"},
        ),
    )

    assert QueriesResolver()(response) == QueryParams({"name": "sam"})


def test_resolver_headers() -> None:
    response: Response = utils.build_response(
        headers={"name": "sam"},
    )

    assert HeadersResolver()(response) == Headers({"name": "sam"})


def test_resolver_cookies() -> None:
    response: Response = utils.build_response(
        headers={"Set-Cookie": "name=sam; Path=/"},
    )

    assert CookiesResolver()(response) == Cookies({"name": "sam"})


def test_resolver_body() -> None:
    response: Response = utils.build_response(
        json={"name": "sam"},
    )

    assert BodyResolver()(response) == {"name": "sam"}


def test_resolver_state() -> None:
    message: str = "Hello, World!"

    response: Response = utils.build_response(
        state=State({"message": message}),
    )

    assert StateResolver("message")(response) == message
