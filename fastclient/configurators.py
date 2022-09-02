from typing import Callable, Optional, TypeVar

from httpx import Cookies, Headers, QueryParams, Timeout
from typing_extensions import ParamSpec

from . import api
from .models import Specification
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


def params(value: QueryParamTypes, /):
    def decorator(func: Callable[PS, RT], /) -> Callable[PS, RT]:
        spec: Optional[Specification] = api.get_specification(func)

        if spec is None:
            raise Exception("Cannot configure callable without a spec")

        spec.request.params = QueryParams(value)

        return func

    return decorator


def headers(value: HeaderTypes, /):
    def decorator(func: Callable[PS, RT], /) -> Callable[PS, RT]:
        spec: Optional[Specification] = api.get_specification(func)

        if spec is None:
            raise Exception("Cannot configure callable without a spec")

        spec.request.headers = Headers(value)

        return func

    return decorator


def cookies(value: CookieTypes, /):
    def decorator(func: Callable[PS, RT], /) -> Callable[PS, RT]:
        spec: Optional[Specification] = api.get_specification(func)

        if spec is None:
            raise Exception("Cannot configure callable without a spec")

        spec.request.cookies = Cookies(value)

        return func

    return decorator


def content(value: RequestContent, /):
    def decorator(func: Callable[PS, RT], /) -> Callable[PS, RT]:
        spec: Optional[Specification] = api.get_specification(func)

        if spec is None:
            raise Exception("Cannot configure callable without a spec")

        spec.request.content = value

        return func

    return decorator


def data(value: RequestData, /):
    def decorator(func: Callable[PS, RT], /) -> Callable[PS, RT]:
        spec: Optional[Specification] = api.get_specification(func)

        if spec is None:
            raise Exception("Cannot configure callable without a spec")

        spec.request.data = value

        return func

    return decorator


def files(value: RequestFiles, /):
    def decorator(func: Callable[PS, RT], /) -> Callable[PS, RT]:
        spec: Optional[Specification] = api.get_specification(func)

        if spec is None:
            raise Exception("Cannot configure callable without a spec")

        spec.request.files = value

        return func

    return decorator


def json(value: JsonTypes, /):
    def decorator(func: Callable[PS, RT], /) -> Callable[PS, RT]:
        spec: Optional[Specification] = api.get_specification(func)

        if spec is None:
            raise Exception("Cannot configure callable without a spec")

        spec.request.json = value

        return func

    return decorator


def timeout(value: TimeoutTypes, /):
    def decorator(func: Callable[PS, RT], /) -> Callable[PS, RT]:
        spec: Optional[Specification] = api.get_specification(func)

        if spec is None:
            raise Exception("Cannot configure callable without a spec")

        spec.request.timeout = Timeout(value)

        return func

    return decorator
