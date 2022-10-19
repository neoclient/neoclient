from typing import Any, Mapping, Protocol, TypeVar

from httpx._utils import primitive_value_to_str
from httpx import (
    QueryParams,
    Headers,
    Cookies,
)

T = TypeVar("T", covariant=True)


class Converter(Protocol[T]):
    def __call__(self, value: Any, /) -> T:
        ...


C = TypeVar("C", bound=Converter)


def converter(func: C, /) -> C:
    return func


@converter
def convert_query_param(value: Any, /) -> str:
    return primitive_value_to_str(value)


@converter
def convert_header(value: Any, /) -> str:
    return primitive_value_to_str(value)


@converter
def convert_cookie(value: Any, /) -> str:
    return primitive_value_to_str(value)


@converter
def convert_path_param(value: Any, /) -> str:
    return primitive_value_to_str(value)


@converter
def convert_query_params(value: Any, /) -> QueryParams:
    return QueryParams(value)


@converter
def convert_headers(value: Any, /) -> Headers:
    return Headers(value)


@converter
def convert_cookies(value: Any, /) -> Cookies:
    return Cookies(value)


@converter
def convert_path_params(value: Any, /) -> Mapping[str, str]:
    return {key: str(value) for key, value in dict(value)}
