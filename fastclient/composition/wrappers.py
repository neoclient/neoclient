from typing import Any, Mapping

from .. import converters
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
from .models import Entry
from .typing import RequestConsumer


def query(key: str, value: Any) -> RequestConsumer:
    return QueryParamComposer(Entry(key, converters.convert_query_param(value)))


def header(key: str, value: Any) -> RequestConsumer:
    return HeaderComposer(Entry(key, converters.convert_header(value)))


def cookie(key: str, value: Any) -> RequestConsumer:
    return CookieComposer(Entry(key, converters.convert_cookie(value)))


def path(key: str, value: Any) -> RequestConsumer:
    return PathParamComposer(Entry(key, converters.convert_path_param(value)))


def query_params(params: QueryParamTypes, /) -> RequestConsumer:
    return QueryParamsComposer(converters.convert_query_params(params))


def headers(headers: HeaderTypes, /) -> RequestConsumer:
    return HeadersComposer(converters.convert_headers(headers))


def cookies(cookies: CookieTypes, /) -> RequestConsumer:
    return CookiesComposer(converters.convert_cookies(cookies))


def path_params(path_params: Mapping[str, Any], /) -> RequestConsumer:
    return PathParamsComposer(converters.convert_path_params(path_params))


def content(content: RequestContent, /) -> RequestConsumer:
    return ContentComposer(content)


def data(data: RequestData, /) -> RequestConsumer:
    return DataComposer(data)


def files(files: RequestFiles, /) -> RequestConsumer:
    return FilesComposer(files)


def json(json: JsonTypes, /) -> RequestConsumer:
    return JsonComposer(json)


def timeout(timeout: TimeoutTypes, /) -> RequestConsumer:
    return TimeoutComposer(converters.convert_timeout(timeout))
