import dataclasses
from dataclasses import replace
from io import BytesIO
from typing import Mapping

from httpx import Cookies, Headers, QueryParams, Timeout
from pytest import fixture

from neoclient.consumers import (
    ContentConsumer,
    CookieConsumer,
    CookiesConsumer,
    DataConsumer,
    FilesConsumer,
    HeaderConsumer,
    HeadersConsumer,
    JsonConsumer,
    PathConsumer,
    PathsConsumer,
    QueriesConsumer,
    QueryConsumer,
    StateConsumer,
    TimeoutConsumer,
)
from neoclient.models import PreRequest, State
from neoclient.types import JsonTypes, RequestContent, RequestData, RequestFiles


@fixture
def pre_request() -> PreRequest:
    return PreRequest("GET", "/foo")


def test_QueryParamConsumer(pre_request: PreRequest) -> None:
    ref_pre_request: PreRequest = replace(pre_request)

    key: str = "name"
    value: str = "sam"

    QueryConsumer(key, value).consume_request(pre_request)

    assert pre_request == replace(ref_pre_request, params={key: value})

    assert QueryConsumer("age", 123) == QueryConsumer("age", "123")


def test_HeaderConsumer(pre_request: PreRequest) -> None:
    ref_pre_request: PreRequest = replace(pre_request)

    key: str = "name"
    value: str = "sam"

    HeaderConsumer(key, value).consume_request(pre_request)

    assert pre_request == replace(ref_pre_request, headers={key: value})

    assert HeaderConsumer("age", 123) == HeaderConsumer("age", "123")


def test_CookieConsumer(pre_request: PreRequest) -> None:
    ref_pre_request: PreRequest = replace(pre_request)

    key: str = "name"
    value: str = "sam"

    CookieConsumer(key, value).consume_request(pre_request)

    assert pre_request == replace(ref_pre_request, cookies={key: value})

    assert CookieConsumer("age", 123) == CookieConsumer("age", "123")


def test_PathParamConsumer(pre_request: PreRequest) -> None:
    ref_pre_request: PreRequest = replace(pre_request)

    key: str = "name"
    value: str = "sam"

    PathConsumer(key, value).consume_request(pre_request)

    assert pre_request == replace(ref_pre_request, path_params={key: value})

    assert PathConsumer("age", 123) == PathConsumer("age", "123")


def test_QueryParamsConsumer(pre_request: PreRequest) -> None:
    ref_pre_request: PreRequest = replace(pre_request)

    params: QueryParams = QueryParams({"name": "sam"})

    QueriesConsumer(params).consume_request(pre_request)

    assert pre_request == replace(ref_pre_request, params=params)

    assert QueriesConsumer({"name": "sam"}) == QueriesConsumer(
        QueryParams({"name": "sam"})
    )


def test_HeadersConsumer(pre_request: PreRequest) -> None:
    ref_pre_request: PreRequest = replace(pre_request)

    headers: Headers = Headers({"name": "sam"})

    HeadersConsumer(headers).consume_request(pre_request)

    assert pre_request == replace(ref_pre_request, headers=headers)

    assert HeadersConsumer({"name": "sam"}) == HeadersConsumer(Headers({"name": "sam"}))


def test_CookiesConsumer(pre_request: PreRequest) -> None:
    ref_pre_request: PreRequest = replace(pre_request)

    cookies: Cookies = Cookies({"name": "sam"})

    CookiesConsumer(cookies).consume_request(pre_request)

    assert pre_request == replace(ref_pre_request, cookies=cookies)

    assert CookiesConsumer({"name": "sam"}) == CookiesConsumer(Cookies({"name": "sam"}))


def test_PathParamsConsumer(pre_request: PreRequest) -> None:
    ref_pre_request: PreRequest = replace(pre_request)

    path_params: Mapping[str, str] = {"name": "sam"}

    PathsConsumer(path_params).consume_request(pre_request)

    assert pre_request == replace(ref_pre_request, path_params=path_params)

    assert PathsConsumer({"age": 123}) == PathsConsumer({"age": "123"})


def test_ContentConsumer(pre_request: PreRequest) -> None:
    ref_pre_request: PreRequest = replace(pre_request)

    content: RequestContent = "content"

    ContentConsumer(content).consume_request(pre_request)

    assert pre_request == replace(ref_pre_request, content=content)


def test_DataConsumer(pre_request: PreRequest) -> None:
    ref_pre_request: PreRequest = replace(pre_request)

    data: RequestData = {"name": "sam"}

    DataConsumer(data).consume_request(pre_request)

    assert pre_request == replace(ref_pre_request, data=data)


def test_FilesConsumer(pre_request: PreRequest) -> None:
    ref_pre_request: PreRequest = replace(pre_request)

    files: RequestFiles = {"file.txt": BytesIO(b"content")}

    FilesConsumer(files).consume_request(pre_request)

    assert pre_request == replace(ref_pre_request, files=files)


def test_JsonConsumer(pre_request: PreRequest) -> None:
    ref_pre_request: PreRequest = replace(pre_request)

    json: JsonTypes = {"name": "sam"}

    JsonConsumer(json).consume_request(pre_request)

    assert pre_request == replace(ref_pre_request, json=json)


def test_TimeoutConsumer(pre_request: PreRequest) -> None:
    ref_pre_request: PreRequest = replace(pre_request)

    timeout: Timeout = Timeout(5.0)

    TimeoutConsumer(timeout).consume_request(pre_request)

    assert pre_request == replace(ref_pre_request, timeout=timeout)

    assert TimeoutConsumer(5.0) == TimeoutConsumer(Timeout(5.0))


def test_StateConsumer(pre_request: PreRequest) -> None:
    ref_pre_request: PreRequest = replace(pre_request)

    message: str = "Hello, World!"

    StateConsumer("message", message).consume_request(pre_request)

    assert pre_request == replace(ref_pre_request, state=State({"message": message}))
