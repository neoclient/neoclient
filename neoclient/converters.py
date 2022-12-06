from http.cookiejar import CookieJar
from typing import Any, Mapping, MutableMapping, MutableSequence, Sequence

from httpx import Cookies, Headers, QueryParams, Timeout
from httpx._utils import primitive_value_to_str

from .errors import ConversionError
from .types import (
    CookiesTypes,
    CookieTypes,
    HeadersTypes,
    HeaderTypes,
    PathsTypes,
    PathTypes,
    Primitive,
    QueriesTypes,
    QueryTypes,
    TimeoutTypes,
)
from .utils import is_primitive

__all__: Sequence[str] = (
    "convert_query_param",
    "convert_header",
    "convert_cookie",
    "convert_path_param",
    "convert_query_params",
    "convert_headers",
    "convert_cookies",
    "convert_path_params",
    "convert_timeout",
)


def convert_query_param(value: QueryTypes, /) -> str:
    if is_primitive(value):
        return primitive_value_to_str(value)
    else:
        return str(value)


def convert_header(value: HeaderTypes, /) -> str:
    if is_primitive(value):
        return primitive_value_to_str(value)
    else:
        return str(value)


def convert_cookie(value: CookieTypes, /) -> str:
    if is_primitive(value):
        return primitive_value_to_str(value)
    else:
        return str(value)


def convert_path_param(value: PathTypes, /) -> str:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return primitive_value_to_str(value)
    elif isinstance(value, Sequence):
        segments: MutableSequence = []

        segment: Primitive
        for segment in value:
            converted_segment: str = primitive_value_to_str(segment)

            if converted_segment:
                segments.append(converted_segment)

        return "/".join(segments)
    else:
        raise ConversionError("path param", value)


def convert_query_params(value: QueriesTypes, /) -> QueryParams:
    if isinstance(value, QueryParams):
        return value
    elif isinstance(value, (Mapping, Sequence)):
        return QueryParams(dict(value))
    else:
        raise ConversionError("query params", value)


def convert_headers(value: HeadersTypes, /) -> Headers:
    if isinstance(value, Headers):
        return value
    elif isinstance(value, (Mapping, Sequence)):
        return Headers(dict(value))
    else:
        raise ConversionError("headers", value)


def convert_cookies(value: CookiesTypes, /) -> Cookies:
    if isinstance(value, Cookies):
        return value
    elif isinstance(value, CookieJar):
        return Cookies(value)
    elif isinstance(value, (Mapping, Sequence)):
        return Cookies(dict(value))
    else:
        raise ConversionError("cookies", value)


def convert_path_params(path_params: PathsTypes, /) -> MutableMapping[str, str]:
    if isinstance(path_params, Mapping):
        return {key: convert_path_param(value) for key, value in path_params.items()}
    else:
        return {key: convert_path_param(value) for key, value in path_params}


def convert_timeout(value: TimeoutTypes, /) -> Timeout:
    return Timeout(value)
