from typing import Callable, Optional, TypeVar

from httpx import Cookies, Headers, QueryParams, Timeout
from typing_extensions import ParamSpec

from .errors import NotAnOperation
from .models import RequestOptions
from .operations import Operation, get_operation
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
        operation: Optional[Operation] = get_operation(func)

        if operation is None:
            raise NotAnOperation(
                f"{func!r} is not an operation, it cannot be composed."
            )

        composer(operation.specification.request)

        return func

    return decorator


def params(value: QueryParamTypes, /) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    def composer(request: RequestOptions, /) -> None:
        request.params = QueryParams(value)

    return _composer(composer)


def headers(value: HeaderTypes, /) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    def composer(request: RequestOptions, /) -> None:
        request.headers = Headers(value)

    return _composer(composer)


def cookies(value: CookieTypes, /) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    def composer(request: RequestOptions, /) -> None:
        request.cookies = Cookies(value)

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
