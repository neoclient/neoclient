from dataclasses import dataclass
from typing import Any, Callable, TypeVar

import param.parameters
from param.typing import Consumer
from httpx import Timeout
from typing_extensions import ParamSpec

from . import composers
from .composers import Composer
from .models import RequestOptions
from .operations import Operation, get_operation
from .parameters import Cookies, Headers, QueryParams, Header
from .types import (
    CookieTypes,
    HeaderTypes,
    JsonTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestFiles,
    TimeoutTypes,
)

PS = ParamSpec("PS")
RT = TypeVar("RT")


def _composer(
    composer: Callable[[RequestOptions], None], /
) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    def decorator(func: Callable[PS, RT], /) -> Callable[PS, RT]:
        operation: Operation = get_operation(func)

        composer(operation.specification.request)

        return func

    return decorator


@dataclass
class Decorator:
    value: Any
    param: param.parameters.Param
    composer: Composer

    def __call__(self, func: Callable[PS, RT], /) -> Callable[PS, RT]:
        operation: Operation = get_operation(func)

        consumer: Consumer[RequestOptions] = self.composer(self.param, self.value)

        consumer(operation.specification.request)

        return func

# TODO: Also implement @param, @cookie, ....
def header(key: str, value: Any, /) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    return Decorator(value, Header(alias=key), composers.compose_header)


def params(value: QueryParamTypes, /) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    return Decorator(value, QueryParams(), composers.compose_query_params)


def headers(value: HeaderTypes, /) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    return Decorator(value, Headers(), composers.compose_headers)


def cookies(value: CookieTypes, /) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    return Decorator(value, Cookies(), composers.compose_cookies)


def content(value: RequestContent, /) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    def composer(request: RequestOptions, /) -> None:
        request.content = value

    return _composer(composer)


def data(value: RequestData, /) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    def composer(request: RequestOptions, /) -> None:
        request.data = value

    return _composer(composer)


def files(value: RequestFiles, /) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    def composer(request: RequestOptions, /) -> None:
        request.files = value

    return _composer(composer)


def json(value: JsonTypes, /) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    def composer(request: RequestOptions, /) -> None:
        request.json = value

    return _composer(composer)


def timeout(value: TimeoutTypes, /) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    def composer(request: RequestOptions, /) -> None:
        request.timeout = Timeout(value)

    return _composer(composer)
