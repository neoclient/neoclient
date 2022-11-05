from dataclasses import replace
from io import BytesIO

from httpx import Cookies, Headers, QueryParams, Timeout
from pytest import fixture

from fastclient import converters, get
from fastclient.composition import decorators
from fastclient.models import RequestOptions
from fastclient.operations import CallableWithOperation
from fastclient.types import (
    CookiesTypes,
    HeadersTypes,
    JsonTypes,
    PathsTypes,
    QueriesTypes,
    RequestContent,
    RequestData,
    RequestFiles,
    TimeoutTypes,
)


@fixture
def func() -> CallableWithOperation:
    @get("/")
    def foo():
        ...

    return foo


def test_query(func: CallableWithOperation) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    key: str = "name"
    value: str = "sam"

    decorators.query(key, value)(func)

    assert func.operation.specification.request == replace(
        original_request, params=QueryParams({key: value})
    )


def test_header(func: CallableWithOperation) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    key: str = "name"
    value: str = "sam"

    decorators.header(key, value)(func)

    assert func.operation.specification.request == replace(
        original_request, headers=Headers({key: value})
    )


def test_cookie(func: CallableWithOperation) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    key: str = "name"
    value: str = "sam"

    decorators.cookie(key, value)(func)

    assert func.operation.specification.request == replace(
        original_request, cookies=Cookies({key: value})
    )


def test_path(func: CallableWithOperation) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    key: str = "name"
    value: str = "sam"

    decorators.path(key, value)(func)

    assert func.operation.specification.request == replace(
        original_request, path_params={key: value}
    )


def test_query_params(func: CallableWithOperation) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    query_params: QueriesTypes = {"name": "sam"}

    decorators.query_params(query_params)(func)

    assert func.operation.specification.request == replace(
        original_request, params=converters.convert_query_params(query_params)
    )


def test_headers(func: CallableWithOperation) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    headers: HeadersTypes = {"name": "sam"}

    decorators.headers(headers)(func)

    assert func.operation.specification.request == replace(
        original_request, headers=converters.convert_headers(headers)
    )


def test_cookies(func: CallableWithOperation) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    cookies: CookiesTypes = {"name": "sam"}

    decorators.cookies(cookies)(func)

    assert func.operation.specification.request == replace(
        original_request, cookies=converters.convert_cookies(cookies)
    )


def test_path_params(func: CallableWithOperation) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    path_params: PathsTypes = {"name": "sam"}

    decorators.path_params(path_params)(func)

    assert func.operation.specification.request == replace(
        original_request, path_params=path_params
    )


def test_content(func: CallableWithOperation) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    content: RequestContent = "content"

    decorators.content(content)(func)

    assert func.operation.specification.request == replace(
        original_request, content=content
    )


def test_data(func: CallableWithOperation) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    data: RequestData = {"name": "sam"}

    decorators.data(data)(func)

    assert func.operation.specification.request == replace(original_request, data=data)


def test_files(func: CallableWithOperation) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    files: RequestFiles = {"file.txt": BytesIO(b"content")}

    decorators.files(files)(func)

    assert func.operation.specification.request == replace(
        original_request, files=files
    )


def test_json(func: CallableWithOperation) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    json: JsonTypes = {"name": "sam"}

    decorators.json(json)(func)

    assert func.operation.specification.request == replace(original_request, json=json)


def test_timeout(func: CallableWithOperation) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    timeout: TimeoutTypes = 5.0

    decorators.timeout(timeout)(func)

    assert func.operation.specification.request == replace(
        original_request, timeout=Timeout(timeout)
    )
