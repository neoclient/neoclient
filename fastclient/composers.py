from typing import Callable, Optional, TypeVar

from httpx import Cookies, Headers, QueryParams, Timeout
from typing_extensions import ParamSpec

from . import api
from .models import OperationSpecification, RequestOptions
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
from .api import Operation

PS = ParamSpec("PS")
RT = TypeVar("RT")


def _composer(
    composer: Callable[[RequestOptions], None], /
) -> Callable[[Operation[PS, RT]], Operation[PS, RT]]:
    def decorator(operation: Operation[PS, RT], /) -> Operation[PS, RT]:
        spec: Optional[OperationSpecification] = api.get_specification(operation.func)

        if spec is None:
            raise Exception("Cannot configure callable without a spec")

        composer(spec.request)

        return operation

    return decorator


def params(
    value: QueryParamTypes, /
) -> Callable[[Operation[PS, RT]], Operation[PS, RT]]:
    def composer(request: RequestOptions, /) -> None:
        request.params = QueryParams(value)

    return _composer(composer)


def headers(value: HeaderTypes, /) -> Callable[[Operation[PS, RT]], Operation[PS, RT]]:
    def composer(request: RequestOptions, /) -> None:
        request.headers = Headers(value)

    return _composer(composer)


def cookies(value: CookieTypes, /) -> Callable[[Operation[PS, RT]], Operation[PS, RT]]:
    def composer(request: RequestOptions, /) -> None:
        request.cookies = Cookies(value)

    return _composer(composer)


def content(
    value: RequestContent, /
) -> Callable[[Operation[PS, RT]], Operation[PS, RT]]:
    def composer(request: RequestOptions, /) -> None:
        request.content = value

    return _composer(composer)


def data(value: RequestData, /) -> Callable[[Operation[PS, RT]], Operation[PS, RT]]:
    def composer(request: RequestOptions, /) -> None:
        request.data = value

    return _composer(composer)


def files(value: RequestFiles, /) -> Callable[[Operation[PS, RT]], Operation[PS, RT]]:
    def composer(request: RequestOptions, /) -> None:
        request.files = value

    return _composer(composer)


def json(value: JsonTypes, /) -> Callable[[Operation[PS, RT]], Operation[PS, RT]]:
    def composer(request: RequestOptions, /) -> None:
        request.json = value

    return _composer(composer)


def timeout(value: TimeoutTypes, /) -> Callable[[Operation[PS, RT]], Operation[PS, RT]]:
    def composer(request: RequestOptions, /) -> None:
        request.timeout = Timeout(value)

    return _composer(composer)
