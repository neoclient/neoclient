from typing import Any, Mapping, Protocol, TypeVar

from httpx._utils import primitive_value_to_str
from httpx import (
    QueryParams,
    Headers,
    Cookies,
    Timeout,
)

from .types import (
    QueryParamTypes,
    HeaderTypes,
    CookieTypes,
    TimeoutTypes,
)

V = TypeVar("V", contravariant=True)
R = TypeVar("R", covariant=True)


class Converter(Protocol[V, R]):
    def __call__(self, value: V, /) -> R:
        ...


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
