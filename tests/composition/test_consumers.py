from dataclasses import replace
from io import BytesIO
from typing import Mapping

from httpx import Cookies, Headers, QueryParams, Timeout
from pytest import fixture

from fastclient.composition.consumers import (
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
    TimeoutConsumer,
)
from fastclient.models import RequestOptions
from fastclient.types import JsonTypes, RequestContent, RequestData, RequestFiles


@fixture
def request_options() -> RequestOptions:
    return RequestOptions("GET", "/foo")


def test_QueryParamConsumer(request_options: RequestOptions) -> None:
    ref_request_options: RequestOptions = replace(request_options)

    key: str = "name"
    value: str = "sam"

    QueryConsumer(key, value)(request_options)

    assert request_options == replace(ref_request_options, params={key: value})

    assert QueryConsumer.parse("age", 123) == QueryConsumer("age", "123")


def test_HeaderConsumer(request_options: RequestOptions) -> None:
    ref_request_options: RequestOptions = replace(request_options)

    key: str = "name"
    value: str = "sam"

    HeaderConsumer(key, value)(request_options)

    assert request_options == replace(ref_request_options, headers={key: value})

    assert HeaderConsumer.parse("age", 123) == HeaderConsumer("age", "123")


def test_CookieConsumer(request_options: RequestOptions) -> None:
    ref_request_options: RequestOptions = replace(request_options)

    key: str = "name"
    value: str = "sam"

    CookieConsumer(key, value)(request_options)

    assert request_options == replace(ref_request_options, cookies={key: value})

    assert CookieConsumer.parse("age", 123) == CookieConsumer("age", "123")


def test_PathParamConsumer(request_options: RequestOptions) -> None:
    ref_request_options: RequestOptions = replace(request_options)

    key: str = "name"
    value: str = "sam"

    PathConsumer(key, value)(request_options)

    assert request_options == replace(ref_request_options, path_params={key: value})

    assert PathConsumer.parse("age", 123) == PathConsumer("age", "123")


def test_QueryParamsConsumer(request_options: RequestOptions) -> None:
    ref_request_options: RequestOptions = replace(request_options)

    params: QueryParams = QueryParams({"name": "sam"})

    QueriesConsumer(params)(request_options)

    assert request_options == replace(ref_request_options, params=params)

    assert QueriesConsumer.parse({"name": "sam"}) == QueriesConsumer(
        QueryParams({"name": "sam"})
    )


def test_HeadersConsumer(request_options: RequestOptions) -> None:
    ref_request_options: RequestOptions = replace(request_options)

    headers: Headers = Headers({"name": "sam"})

    HeadersConsumer(headers)(request_options)

    assert request_options == replace(ref_request_options, headers=headers)

    assert HeadersConsumer.parse({"name": "sam"}) == HeadersConsumer(
        Headers({"name": "sam"})
    )


def test_CookiesConsumer(request_options: RequestOptions) -> None:
    ref_request_options: RequestOptions = replace(request_options)

    cookies: Cookies = Cookies({"name": "sam"})

    CookiesConsumer(cookies)(request_options)

    assert request_options == replace(ref_request_options, cookies=cookies)

    assert CookiesConsumer.parse({"name": "sam"}) == CookiesConsumer(
        Cookies({"name": "sam"})
    )


def test_PathParamsConsumer(request_options: RequestOptions) -> None:
    ref_request_options: RequestOptions = replace(request_options)

    path_params: Mapping[str, str] = {"name": "sam"}

    PathsConsumer(path_params)(request_options)

    assert request_options == replace(ref_request_options, path_params=path_params)

    assert PathsConsumer.parse({"age": 123}) == PathsConsumer({"age": "123"})


def test_ContentConsumer(request_options: RequestOptions) -> None:
    ref_request_options: RequestOptions = replace(request_options)

    content: RequestContent = "content"

    ContentConsumer(content)(request_options)

    assert request_options == replace(ref_request_options, content=content)


def test_DataConsumer(request_options: RequestOptions) -> None:
    ref_request_options: RequestOptions = replace(request_options)

    data: RequestData = {"name": "sam"}

    DataConsumer(data)(request_options)

    assert request_options == replace(ref_request_options, data=data)


def test_FilesConsumer(request_options: RequestOptions) -> None:
    ref_request_options: RequestOptions = replace(request_options)

    files: RequestFiles = {"file.txt": BytesIO(b"content")}

    FilesConsumer(files)(request_options)

    assert request_options == replace(ref_request_options, files=files)


def test_JsonConsumer(request_options: RequestOptions) -> None:
    ref_request_options: RequestOptions = replace(request_options)

    json: JsonTypes = {"name": "sam"}

    JsonConsumer(json)(request_options)

    assert request_options == replace(ref_request_options, json=json)


def test_TimeoutConsumer(request_options: RequestOptions) -> None:
    ref_request_options: RequestOptions = replace(request_options)

    timeout: Timeout = Timeout(5.0)

    TimeoutConsumer(timeout)(request_options)

    assert request_options == replace(ref_request_options, timeout=timeout)

    assert TimeoutConsumer.parse(5.0) == TimeoutConsumer(Timeout(5.0))
