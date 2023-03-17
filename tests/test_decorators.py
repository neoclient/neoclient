from dataclasses import replace
from io import BytesIO
from typing import Callable, Type

from httpx import Cookies, Headers, QueryParams, Timeout
from pytest import fixture

from neoclient import converters, decorators, get
from neoclient.middleware import RequestMiddleware
from neoclient.models import ClientOptions, PreRequest, Request, Response
from neoclient.operation import get_operation
from neoclient.service import Service
from neoclient.types import (
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
def func() -> Callable:
    @get("/foo")
    def foo():
        ...

    return foo


@fixture
def service() -> Type[Service]:
    class SomeService(Service):
        @get("/foo")
        def foo(self):
            ...

    return SomeService


def test_query(func: Callable) -> None:
    original_request: PreRequest = replace(get_operation(func).specification.request)

    key: str = "name"
    value: str = "sam"

    decorators.query(key, value)(func)

    assert get_operation(func).specification.request == replace(
        original_request, params=QueryParams({key: value})
    )


def test_header(func: Callable) -> None:
    original_request: PreRequest = replace(get_operation(func).specification.request)

    key: str = "name"
    value: str = "sam"

    decorators.header(key, value)(func)

    assert get_operation(func).specification.request == replace(
        original_request, headers=Headers({key: value})
    )


def test_cookie(func: Callable) -> None:
    original_request: PreRequest = replace(get_operation(func).specification.request)

    key: str = "name"
    value: str = "sam"

    decorators.cookie(key, value)(func)

    assert get_operation(func).specification.request == replace(
        original_request, cookies=Cookies({key: value})
    )


def test_path(func: Callable) -> None:
    original_request: PreRequest = replace(get_operation(func).specification.request)

    key: str = "name"
    value: str = "sam"

    decorators.path(key, value)(func)

    assert get_operation(func).specification.request == replace(
        original_request, path_params={key: value}
    )


def test_query_params(func: Callable) -> None:
    original_request: PreRequest = replace(get_operation(func).specification.request)

    query_params: QueriesTypes = {"name": "sam"}

    decorators.query_params(query_params)(func)

    assert get_operation(func).specification.request == replace(
        original_request, params=converters.convert_query_params(query_params)
    )


def test_headers(func: Callable) -> None:
    original_request: PreRequest = replace(get_operation(func).specification.request)

    headers: HeadersTypes = {"name": "sam"}

    decorators.headers(headers)(func)

    assert get_operation(func).specification.request == replace(
        original_request, headers=converters.convert_headers(headers)
    )


def test_cookies(func: Callable) -> None:
    original_request: PreRequest = replace(get_operation(func).specification.request)

    cookies: CookiesTypes = {"name": "sam"}

    decorators.cookies(cookies)(func)

    assert get_operation(func).specification.request == replace(
        original_request, cookies=converters.convert_cookies(cookies)
    )


def test_path_params(func: Callable) -> None:
    original_request: PreRequest = replace(get_operation(func).specification.request)

    path_params: PathsTypes = {"name": "sam"}

    decorators.path_params(path_params)(func)

    assert get_operation(func).specification.request == replace(
        original_request, path_params=path_params
    )


def test_content(func: Callable) -> None:
    original_request: PreRequest = replace(get_operation(func).specification.request)

    content: RequestContent = "content"

    decorators.content(content)(func)

    assert get_operation(func).specification.request == replace(
        original_request, content=content
    )


def test_data(func: Callable) -> None:
    original_request: PreRequest = replace(get_operation(func).specification.request)

    data: RequestData = {"name": "sam"}

    decorators.data(data)(func)

    assert get_operation(func).specification.request == replace(
        original_request, data=data
    )


def test_files(func: Callable) -> None:
    original_request: PreRequest = replace(get_operation(func).specification.request)

    files: RequestFiles = {"file.txt": BytesIO(b"content")}

    decorators.files(files)(func)

    assert get_operation(func).specification.request == replace(
        original_request, files=files
    )


def test_json(func: Callable) -> None:
    original_request: PreRequest = replace(get_operation(func).specification.request)

    json: JsonTypes = {"name": "sam"}

    decorators.json(json)(func)

    assert get_operation(func).specification.request == replace(
        original_request, json=json
    )


def test_timeout(func: Callable) -> None:
    original_request: PreRequest = replace(get_operation(func).specification.request)

    timeout: TimeoutTypes = 5.0

    decorators.timeout(timeout)(func)

    assert get_operation(func).specification.request == replace(
        original_request, timeout=Timeout(timeout)
    )


def test_mount(func: Callable) -> None:
    original_request: PreRequest = replace(get_operation(func).specification.request)

    mount: str = "/mount"

    decorators.mount(mount)(func)

    assert get_operation(func).specification.request == replace(
        original_request, url="/mount/foo"
    )


def test_base_url(service: Type[Service]) -> None:
    original_client_options: ClientOptions = replace(service._spec.options)

    base_url: str = "https://foo.bar/"

    decorators.base_url(base_url)(service)

    assert service._spec.options == replace(
        original_client_options, base_url="https://foo.bar/"
    )


def test_middleware(func: Callable) -> None:
    def middleware_foo(call_next: RequestMiddleware, request: Request) -> Response:
        return call_next(request)

    def middleware_bar(call_next: RequestMiddleware, request: Request) -> Response:
        return call_next(request)

    decorators.middleware(middleware_foo)(func)
    decorators.middleware(middleware_bar)(func)

    assert get_operation(func).specification.middleware.record == [
        middleware_foo,
        middleware_bar,
    ]


def test_user_agent(func: Callable) -> None:
    original_request: PreRequest = replace(get_operation(func).specification.request)

    user_agent: str = "foo/1.0"

    decorators.user_agent(user_agent)(func)

    assert get_operation(func).specification.request == replace(
        original_request, headers=Headers({"User-Agent": user_agent})
    )


def test_accept(func: Callable) -> None:
    original_request: PreRequest = replace(get_operation(func).specification.request)

    accept: str = "en-GB"

    decorators.accept(accept)(func)

    assert get_operation(func).specification.request == replace(
        original_request, headers=Headers({"Accept": accept})
    )


def test_referer(func: Callable) -> None:
    original_request: PreRequest = replace(get_operation(func).specification.request)

    referer: str = "https://foo.bar/"

    decorators.referer(referer)(func)

    assert get_operation(func).specification.request == replace(
        original_request, headers=Headers({"Referer": referer})
    )
