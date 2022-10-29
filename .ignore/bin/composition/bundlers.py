from typing import Any, Mapping

from httpx import Cookies, Headers, QueryParams, Timeout

from .. import converters
from ..types import (CookieTypes, HeaderTypes, JsonTypes, QueryParamTypes,
                     RequestContent, RequestData, RequestFiles, TimeoutTypes)
from .models import Entry


def query(key: str, value: Any) -> Entry[str, str]:
    return Entry(key, converters.convert_query_param(value))


def header(key: str, value: Any) -> Entry[str, str]:
    return Entry(key, converters.convert_header(value))


def cookie(key: str, value: Any) -> Entry[str, str]:
    return Entry(key, converters.convert_cookie(value))


def path(key: str, value: Any) -> Entry[str, str]:
    return Entry(key, converters.convert_path_param(value))


def query_params(params: QueryParamTypes, /) -> QueryParams:
    return converters.convert_query_params(params)


def headers(headers: HeaderTypes, /) -> Headers:
    return converters.convert_headers(headers)


def cookies(cookies: CookieTypes, /) -> Cookies:
    return converters.convert_cookies(cookies)


def path_params(path_params: Mapping[str, Any], /) -> Mapping[str, str]:
    return converters.convert_path_params(path_params)


def content(content: RequestContent, /) -> RequestContent:
    return content


def data(data: RequestData, /) -> RequestData:
    return data


def files(files: RequestFiles, /) -> RequestFiles:
    return files


def json(json: JsonTypes, /) -> JsonTypes:
    return json


def timeout(timeout: TimeoutTypes, /) -> Timeout:
    return converters.convert_timeout(timeout)
