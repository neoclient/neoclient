from typing import Callable, TypeVar

from httpx import Timeout
from typing_extensions import ParamSpec

from .models import RequestOptions
from .operations import Operation, get_operation, add_query_params, add_headers, add_cookies
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


def params(value: QueryParamTypes, /) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    def composer(request: RequestOptions, /) -> None:
        add_query_params(request, value)

    return _composer(composer)


def headers(value: HeaderTypes, /) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    def composer(request: RequestOptions, /) -> None:
        add_headers(request, value)

    return _composer(composer)


def cookies(value: CookieTypes, /) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    def composer(request: RequestOptions, /) -> None:
        add_cookies(request, value)

    return _composer(composer)


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
