from typing import Any, Mapping

from ..types import (
    CookieTypes,
    HeaderTypes,
    JsonTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestFiles,
    TimeoutTypes,
)
from . import bundlers
from .factories import (
    ContentComposer,
    CookieComposer,
    CookiesComposer,
    DataComposer,
    FilesComposer,
    HeaderComposer,
    HeadersComposer,
    JsonComposer,
    PathParamComposer,
    PathParamsComposer,
    QueryParamComposer,
    QueryParamsComposer,
    TimeoutComposer,
)
from .typing import RequestConsumer


def query(key: str, value: Any) -> RequestConsumer:
    return QueryParamComposer(bundlers.query(key, value))


def header(key: str, value: Any) -> RequestConsumer:
    return HeaderComposer(bundlers.header(key, value))


def cookie(key: str, value: Any) -> RequestConsumer:
    return CookieComposer(bundlers.cookie(key, value))


def path(key: str, value: Any) -> RequestConsumer:
    return PathParamComposer(bundlers.path(key, value))


def query_params(params: QueryParamTypes, /) -> RequestConsumer:
    return QueryParamsComposer(bundlers.query_params(params))


def headers(headers: HeaderTypes, /) -> RequestConsumer:
    return HeadersComposer(bundlers.headers(headers))


def cookies(cookies: CookieTypes, /) -> RequestConsumer:
    return CookiesComposer(bundlers.cookies(cookies))


def path_params(path_params: Mapping[str, Any], /) -> RequestConsumer:
    return PathParamsComposer(bundlers.path_params(path_params))


def content(content: RequestContent, /) -> RequestConsumer:
    return ContentComposer(bundlers.content(content))


def data(data: RequestData, /) -> RequestConsumer:
    return DataComposer(bundlers.data(data))


def files(files: RequestFiles, /) -> RequestConsumer:
    return FilesComposer(bundlers.files(files))


def json(json: JsonTypes, /) -> RequestConsumer:
    return JsonComposer(bundlers.json(json))


def timeout(timeout: TimeoutTypes, /) -> RequestConsumer:
    return TimeoutComposer(bundlers.timeout(timeout))
