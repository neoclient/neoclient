from typing import Any, Mapping

from httpx import Cookies, Headers, QueryParams, Timeout
from httpx._utils import primitive_value_to_str

from .types import CookieTypes, HeaderTypes, QueryParamTypes, TimeoutTypes


def convert_query_param(value: Any, /) -> str:
    return primitive_value_to_str(value)


def convert_header(value: Any, /) -> str:
    return primitive_value_to_str(value)


def convert_cookie(value: Any, /) -> str:
    return primitive_value_to_str(value)


def convert_path_param(value: Any, /) -> str:
    return primitive_value_to_str(value)


def convert_query_params(value: QueryParamTypes, /) -> QueryParams:
    return QueryParams(value)


def convert_headers(value: HeaderTypes, /) -> Headers:
    return Headers(value)


def convert_cookies(value: CookieTypes, /) -> Cookies:
    return Cookies(value)


def convert_path_params(value: Mapping[str, Any], /) -> Mapping[str, str]:
    return {key: primitive_value_to_str(value) for key, value in value.items()}


def convert_timeout(value: TimeoutTypes, /) -> Timeout:
    return Timeout(value)
