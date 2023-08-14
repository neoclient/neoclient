from httpx import Cookies, Headers, QueryParams

from neoclient.models import PreRequest, Response, State
from neoclient.resolvers import (
    BodyResolver,
    CookieResolver,
    CookiesResolver,
    HeaderResolver,
    HeadersResolver,
    QueryParamsResolver,
    QueryResolver,
    StateResolver,
)

from . import utils


def test_QueryResolver_resolve_request() -> None:
    request_with_param: PreRequest = utils.build_pre_request(
        params={"name": "sam"},
    )
    request_without_param: PreRequest = utils.build_pre_request()

    assert QueryResolver("name").resolve_request(request_with_param) == ["sam"]
    assert QueryResolver("name").resolve_request(request_without_param) is None


def test_QueryResolver_resolve_response() -> None:
    response_with_param: Response = utils.build_response(
        request=utils.build_request(
            params={"name": "sam"},
        )
    )
    response_without_param: Response = utils.build_response()

    assert QueryResolver("name").resolve_response(response_with_param) == ["sam"]
    assert QueryResolver("name").resolve_response(response_without_param) is None


def test_HeaderResolver_resolve_request() -> None:
    request_with_header: PreRequest = utils.build_pre_request(
        headers={"name": "sam"},
    )
    request_without_header: PreRequest = utils.build_pre_request()

    assert HeaderResolver("name").resolve_request(request_with_header) == ["sam"]
    assert HeaderResolver("name").resolve_request(request_without_header) is None


def test_HeaderResolver_resolve_response() -> None:
    response_with_header: Response = utils.build_response(
        headers={"name": "sam"},
    )
    response_without_header: Response = utils.build_response()

    assert HeaderResolver("name").resolve_response(response_with_header) == ["sam"]
    assert HeaderResolver("name").resolve_response(response_without_header) is None


def test_CookieResolver_resolve_request() -> None:
    request_with_cookie: PreRequest = utils.build_pre_request(
        cookies={"name": "sam"},
    )
    request_without_cookie: PreRequest = utils.build_pre_request()

    assert CookieResolver("name").resolve_request(request_with_cookie) == "sam"
    assert CookieResolver("name").resolve_request(request_without_cookie) is None


def test_CookieResolver_resolve_response() -> None:
    response_with_cookie: Response = utils.build_response(
        headers={"Set-Cookie": "name=sam; Path=/"},
    )
    response_without_cookie: Response = utils.build_response()

    assert CookieResolver("name").resolve_response(response_with_cookie) == "sam"
    assert CookieResolver("name").resolve_response(response_without_cookie) is None


def test_QueryParamsResolver_resolve_request() -> None:
    request: PreRequest = utils.build_pre_request(
        params={"name": "sam"},
    )

    assert QueryParamsResolver().resolve_request(request) == QueryParams(
        {"name": "sam"}
    )


def test_QueryParamsResolver_resolve_response() -> None:
    response: Response = utils.build_response(
        request=utils.build_request(
            params={"name": "sam"},
        ),
    )

    assert QueryParamsResolver().resolve_response(response) == QueryParams(
        {"name": "sam"}
    )


def test_HeadersResolver_resolve_request() -> None:
    request: PreRequest = utils.build_pre_request(
        headers={"name": "sam"},
    )

    assert HeadersResolver().resolve_request(request) == Headers({"name": "sam"})


def test_HeadersResolver_resolve_response() -> None:
    response: Response = utils.build_response(
        headers={"name": "sam"},
    )

    assert HeadersResolver().resolve_response(response) == Headers({"name": "sam"})


def test_CookiesResolver_resolve_request() -> None:
    request: PreRequest = utils.build_pre_request(
        cookies={"name": "sam"},
    )

    assert CookiesResolver().resolve_request(request) == Cookies({"name": "sam"})


def test_CookiesResolver_resolve_response() -> None:
    response: Response = utils.build_response(
        headers={"Set-Cookie": "name=sam; Path=/"},
    )

    assert CookiesResolver().resolve_response(response) == Cookies({"name": "sam"})


def test_BodyResolver() -> None:
    response: Response = utils.build_response(
        json={"name": "sam"},
    )

    assert BodyResolver()(response) == {"name": "sam"}


def test_StateResolver_resolve_request() -> None:
    message: str = "Hello, World!"

    request: PreRequest = utils.build_pre_request(
        state=State({"message": message}),
    )

    assert StateResolver("message").resolve_request(request) == message


def test_StateResolver_resolve_response() -> None:
    message: str = "Hello, World!"

    response: Response = utils.build_response(
        state=State({"message": message}),
    )

    assert StateResolver("message").resolve_response(response) == message
