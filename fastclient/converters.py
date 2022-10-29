from typing import Any, Collection, Mapping

from httpx import Cookies, Headers, QueryParams, Timeout
from httpx._utils import primitive_value_to_str

from .typs import PathParams
from .types import (
    CookieTypes,
    HeaderTypes,
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


def convert_path_param(value: Any, /) -> str:
    return primitive_value_to_str(value)


def convert_query_params(value: QueryParamTypes, /) -> QueryParams:
    return QueryParams(value)


def convert_headers(value: HeaderTypes, /) -> Headers:
    return Headers(value)


def convert_cookies(value: CookieTypes, /) -> Cookies:
    return Cookies(value)


def convert_path_params(path_params: PathParamTypes, /) -> PathParams:
    # return PathParams(value)

    if isinstance(path_params, PathParams):
        return path_params
    elif isinstance(path_params, Mapping):
        return PathParams(
            kwargs={
                key: primitive_value_to_str(value)
                for key, value in path_params.items()
            },
        )
    elif isinstance(path_params, Collection):
        return PathParams(
            args=[
                primitive_value_to_str(value)
                for value in path_params
            ],
        )
    else:
        raise ValueError(f"Failed to convert path params {path_params!r}, unsupported type.")


def convert_timeout(value: TimeoutTypes, /) -> Timeout:
    return Timeout(value)
