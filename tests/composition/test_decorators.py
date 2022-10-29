from dataclasses import replace
from io import BytesIO
from typing import Any, Callable, Mapping

from pytest import fixture
from httpx import (
    QueryParams,
    Headers,
    Cookies,
    Timeout,
)

from fastclient import get
from fastclient.models import RequestOptions
from fastclient.composition import decorators
from fastclient.types import (
    JsonTypes,
    QueryParamTypes,
    HeaderTypes,
    CookieTypes,
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

    decorators.query(key, value)(func)

    assert func.operation.specification.request == replace(
        original_request, params=QueryParams({key: value})
    )


def test_header(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    key: str = "name"
    value: str = "sam"

    decorators.header(key, value)(func)

    assert func.operation.specification.request == replace(
        original_request, headers=Headers({key: value})
    )


def test_cookie(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    key: str = "name"
    value: str = "sam"

    decorators.cookie(key, value)(func)

    assert func.operation.specification.request == replace(
        original_request, cookies=Cookies({key: value})
    )


def test_path(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    key: str = "name"
    value: str = "sam"

    decorators.path(key, value)(func)

    assert func.operation.specification.request == replace(
        original_request, path_params={key: value}
    )


def test_query_params(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    query_params: QueryParamTypes = {"name": "sam"}

    decorators.query_params(query_params)(func)

    assert func.operation.specification.request == replace(
        original_request, params=QueryParams(query_params)
    )


def test_headers(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    headers: HeaderTypes = {"name": "sam"}

    decorators.headers(headers)(func)

    assert func.operation.specification.request == replace(
        original_request, headers=Headers(headers)
    )


def test_cookies(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    cookies: CookieTypes = {"name": "sam"}

    decorators.cookies(cookies)(func)

    assert func.operation.specification.request == replace(
        original_request, cookies=Cookies(cookies)
    )


def test_path_params(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    path_params: Mapping[str, str] = {"name": "sam"}

    decorators.path_params(path_params)(func)

    assert func.operation.specification.request == replace(
        original_request, path_params=path_params
    )


def test_content(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    content: RequestContent = "content"

    decorators.content(content)(func)

    assert func.operation.specification.request == replace(
        original_request, content=content
    )


def test_data(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    data: RequestData = {"name": "sam"}

    decorators.data(data)(func)

    assert func.operation.specification.request == replace(original_request, data=data)


def test_files(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    files: RequestFiles = {"file.txt": BytesIO(b"content")}

    decorators.files(files)(func)

    assert func.operation.specification.request == replace(
        original_request, files=files
    )


def test_json(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    json: JsonTypes = {"name": "sam"}

    decorators.json(json)(func)

    assert func.operation.specification.request == replace(original_request, json=json)


def test_timeout(func: Callable) -> None:
    original_request: RequestOptions = replace(func.operation.specification.request)

    timeout: TimeoutTypes = 5.0

    decorators.timeout(timeout)(func)

    assert func.operation.specification.request == replace(
        original_request, timeout=Timeout(timeout)
    )
