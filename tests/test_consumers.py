from dataclasses import replace
from io import BytesIO
from typing import Mapping, MutableMapping

from httpx import Cookies, Headers, QueryParams, Timeout
from pytest import fixture

from neoclient.consumers import (
    ContentConsumer,
    CookieConsumer,
    CookiesConsumer,
    DataConsumer,
    FilesConsumer,
    FollowRedirectsConsumer,
    HeaderConsumer,
    HeadersConsumer,
    JsonConsumer,
    PathConsumer,
    PathParamsConsumer,
    QueryConsumer,
    QueryParamsConsumer,
    StateConsumer,
    TimeoutConsumer,
)
from neoclient.defaults import DEFAULT_FOLLOW_REDIRECTS
from neoclient.models import RequestOpts, State
from neoclient.types import JsonTypes, RequestContent, RequestData, RequestFiles


@fixture
def pre_request() -> RequestOpts:
    return RequestOpts("GET", "/foo")


def test_consumer_query_param(pre_request: RequestOpts) -> None:
    key: str = "name"
    value: str = "sam"

    expected_pre_request: RequestOpts = pre_request.copy()
    expected_pre_request.params = QueryParams({key: value})

    QueryConsumer(key, value).consume_request(pre_request)

    assert pre_request == expected_pre_request

    assert QueryConsumer("age", 123) == QueryConsumer("age", "123")


def test_consumer_header(pre_request: RequestOpts) -> None:
    key: str = "name"
    value: str = "sam"

    expected_pre_request: RequestOpts = pre_request.copy()
    expected_pre_request.headers = Headers({key: value})

    HeaderConsumer(key, value).consume_request(pre_request)

    assert pre_request == expected_pre_request

    assert HeaderConsumer("age", 123) == HeaderConsumer("age", "123")


def test_consumer_cookie(pre_request: RequestOpts) -> None:
    key: str = "name"
    value: str = "sam"

    expected_pre_request: RequestOpts = pre_request.copy()
    expected_pre_request.cookies = Cookies({key: value})

    CookieConsumer(key, value).consume_request(pre_request)

    assert pre_request == expected_pre_request

    assert CookieConsumer("age", 123) == CookieConsumer("age", "123")


def test_consumer_path_param(pre_request: RequestOpts) -> None:
    key: str = "name"
    value: str = "sam"

    expected_pre_request: RequestOpts = pre_request.copy()
    expected_pre_request.path_params = {key: value}

    PathConsumer(key, value).consume_request(pre_request)

    assert pre_request == expected_pre_request

    assert PathConsumer("age", 123) == PathConsumer("age", "123")


def test_consumer_query_params(pre_request: RequestOpts) -> None:
    params: QueryParams = QueryParams({"name": "sam"})

    expected_pre_request: RequestOpts = pre_request.copy()
    expected_pre_request.params = params

    QueryParamsConsumer(params).consume_request(pre_request)

    assert pre_request == expected_pre_request

    assert QueryParamsConsumer({"name": "sam"}) == QueryParamsConsumer(
        QueryParams({"name": "sam"})
    )


def test_consumer_headers(pre_request: RequestOpts) -> None:
    headers: Headers = Headers({"name": "sam"})

    expected_pre_request: RequestOpts = pre_request.copy()
    expected_pre_request.headers = headers

    HeadersConsumer(headers).consume_request(pre_request)

    assert pre_request == expected_pre_request

    assert HeadersConsumer({"name": "sam"}) == HeadersConsumer(Headers({"name": "sam"}))


def test_consumer_cookies(pre_request: RequestOpts) -> None:
    cookies: Cookies = Cookies({"name": "sam"})

    expected_pre_request: RequestOpts = pre_request.copy()
    expected_pre_request.cookies = cookies

    CookiesConsumer(cookies).consume_request(pre_request)

    assert pre_request == expected_pre_request

    assert CookiesConsumer({"name": "sam"}) == CookiesConsumer(Cookies({"name": "sam"}))


def test_consumer_path_params(pre_request: RequestOpts) -> None:
    path_params: MutableMapping[str, str] = {"name": "sam"}

    expected_pre_request: RequestOpts = pre_request.copy()
    expected_pre_request.path_params = path_params

    PathParamsConsumer(path_params).consume_request(pre_request)

    assert pre_request == expected_pre_request


def test_consumer_content(pre_request: RequestOpts) -> None:
    content: RequestContent = "content"

    expected_pre_request: RequestOpts = pre_request.copy()
    expected_pre_request.content = content

    ContentConsumer(content).consume_request(pre_request)

    assert pre_request == expected_pre_request


def test_consumer_data(pre_request: RequestOpts) -> None:
    data: RequestData = {"name": "sam"}

    expected_pre_request: RequestOpts = pre_request.copy()
    expected_pre_request.data = data

    DataConsumer(data).consume_request(pre_request)

    assert pre_request == expected_pre_request


def test_consumer_files(pre_request: RequestOpts) -> None:
    files: RequestFiles = {"file.txt": BytesIO(b"content")}

    expected_pre_request: RequestOpts = pre_request.copy()
    expected_pre_request.files = files

    FilesConsumer(files).consume_request(pre_request)

    assert pre_request == expected_pre_request


def test_consumer_json(pre_request: RequestOpts) -> None:
    json: JsonTypes = {"name": "sam"}

    expected_pre_request: RequestOpts = pre_request.copy()
    expected_pre_request.json = json

    JsonConsumer(json).consume_request(pre_request)

    assert pre_request == expected_pre_request


def test_consumer_timeout(pre_request: RequestOpts) -> None:
    timeout: Timeout = Timeout(5.0)

    expected_pre_request: RequestOpts = pre_request.copy()
    expected_pre_request.timeout = timeout

    TimeoutConsumer(timeout).consume_request(pre_request)

    assert pre_request == expected_pre_request

    assert TimeoutConsumer(5.0) == TimeoutConsumer(Timeout(5.0))


def test_consumer_state(pre_request: RequestOpts) -> None:
    message: str = "Hello, World!"

    expected_pre_request: RequestOpts = pre_request.copy()
    expected_pre_request.state = State({"message": message})

    StateConsumer("message", message).consume_request(pre_request)

    assert pre_request == expected_pre_request


def test_FollowRedirectsConsumer(pre_request: RequestOpts) -> None:
    follow_redirects: bool = not DEFAULT_FOLLOW_REDIRECTS

    expected_pre_request: RequestOpts = pre_request.copy()
    expected_pre_request.follow_redirects = follow_redirects

    FollowRedirectsConsumer(follow_redirects).consume_request(pre_request)

    assert pre_request == expected_pre_request
