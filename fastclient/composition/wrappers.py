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
from .typing import Composer


def query(key: str, value: Any) -> Composer:
    return QueryParamComposer(Entry(key, converters.convert_query_param(value)))


def header(key: str, value: Any) -> Composer:
    return HeaderComposer(Entry(key, converters.convert_header(value)))


def cookie(key: str, value: Any) -> Composer:
    return CookieComposer(Entry(key, converters.convert_cookie(value)))


def path(key: str, value: Any) -> Composer:
    return PathParamComposer(Entry(key, converters.convert_path_param(value)))


def query_params(params: QueryParamTypes, /) -> Composer:
    return QueryParamsComposer(converters.convert_query_params(params))


def headers(headers: HeaderTypes, /) -> Composer:
    return HeadersComposer(converters.convert_headers(headers))


def cookies(cookies: CookieTypes, /) -> Composer:
    return CookiesComposer(converters.convert_cookies(cookies))


def path_params(path_params: Mapping[str, Any], /) -> Composer:
    return PathParamsComposer(converters.convert_path_params(path_params))


def content(content: RequestContent, /) -> Composer:
    return ContentComposer(content)


def data(data: RequestData, /) -> Composer:
    return DataComposer(data)


def files(files: RequestFiles, /) -> Composer:
    return FilesComposer(files)


def json(json: JsonTypes, /) -> Composer:
    return JsonComposer(json)


def timeout(timeout: TimeoutTypes, /) -> Composer:
    return TimeoutComposer(converters.convert_timeout(timeout))
