from dataclasses import replace
from io import BytesIO
from typing import Any, Callable, Mapping

from httpx import Cookies, Headers, QueryParams, Timeout
from pytest import fixture

from fastclient import get
from fastclient.composition.composition import composition_decorators
from fastclient.models import RequestOptions
from fastclient.types import (
    CookieTypes,
    HeaderTypes,
    JsonTypes,
    PathParamTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestFiles,
    TimeoutTypes,
)


@fixture
def func() -> Callable:
    @get("/")
    def foo():
        ...

    return foo


def test_query(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    key: str = "name"
    value: str = "sam"

    composition_decorators.query(key, value)(func)

    assert func.operation.specification.request == replace(
        original_request, params=QueryParams({key: value})
    )


def test_header(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    key: str = "name"
    value: str = "sam"

    composition_decorators.header(key, value)(func)

    assert func.operation.specification.request == replace(
        original_request, headers=Headers({key: value})
    )


def test_cookie(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    key: str = "name"
    value: str = "sam"

    composition_decorators.cookie(key, value)(func)

    assert func.operation.specification.request == replace(
        original_request, cookies=Cookies({key: value})
    )


def test_path(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    key: str = "name"
    value: str = "sam"

    composition_decorators.path(key, value)(func)

    assert func.operation.specification.request == replace(
        original_request, path_params={key: value}
    )


def test_query_params(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    query_params: QueryParamTypes = {"name": "sam"}

    composition_decorators.query_params(query_params)(func)

    assert func.operation.specification.request == replace(
        original_request, params=QueryParams(query_params)
    )


def test_headers(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    headers: HeaderTypes = {"name": "sam"}

    composition_decorators.headers(headers)(func)

    assert func.operation.specification.request == replace(
        original_request, headers=Headers(headers)
    )


def test_cookies(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    cookies: CookieTypes = {"name": "sam"}

    composition_decorators.cookies(cookies)(func)

    assert func.operation.specification.request == replace(
        original_request, cookies=Cookies(cookies)
    )


def test_path_params(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    path_params: PathParamTypes = {"name": "sam"}

    composition_decorators.path_params(path_params)(func)

    assert func.operation.specification.request == replace(
        original_request, path_params=path_params
    )


def test_content(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    content: RequestContent = "content"

    composition_decorators.content(content)(func)

    assert func.operation.specification.request == replace(
        original_request, content=content
    )


def test_data(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    data: RequestData = {"name": "sam"}

    composition_decorators.data(data)(func)

    assert func.operation.specification.request == replace(original_request, data=data)


def test_files(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    files: RequestFiles = {"file.txt": BytesIO(b"content")}

    composition_decorators.files(files)(func)

    assert func.operation.specification.request == replace(
        original_request, files=files
    )


def test_json(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    json: JsonTypes = {"name": "sam"}

    composition_decorators.json(json)(func)

    assert func.operation.specification.request == replace(original_request, json=json)


def test_timeout(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    timeout: TimeoutTypes = 5.0

    composition_decorators.timeout(timeout)(func)

    assert func.operation.specification.request == replace(
        original_request, timeout=Timeout(timeout)
    )
