from typing import Any, MutableMapping

from httpx import Cookies, Headers, QueryParams, Timeout
from httpx._utils import primitive_value_to_str

from .types import (
    CookieTypes,
    HeaderTypes,
    PathParamValueTypes,
    QueryParamTypes,
    TimeoutTypes,
    PathParamTypes,
)


def convert_query_param(value: Any, /) -> str:
    return primitive_value_to_str(value)


def convert_header(value: Any, /) -> str:
    return primitive_value_to_str(value)


def convert_cookie(value: Any, /) -> str:
    return primitive_value_to_str(value)


def convert_path_param(value: PathParamValueTypes, /) -> str:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return primitive_value_to_str(value)
    else:
        return "/".join(primitive_value_to_str(v) for v in value)


def convert_query_params(value: QueryParamTypes, /) -> QueryParams:
    return QueryParams(value)


def convert_headers(value: HeaderTypes, /) -> Headers:
    return Headers(value)


def convert_cookies(value: CookieTypes, /) -> Cookies:
    return Cookies(value)


def convert_path_params(path_params: PathParamTypes, /) -> MutableMapping[str, str]:
    return {key: convert_path_param(value) for key, value in path_params.items()}


def convert_timeout(value: TimeoutTypes, /) -> Timeout:
    return Timeout(value)
