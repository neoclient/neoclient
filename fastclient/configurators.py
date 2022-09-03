from typing import Optional, TypeVar

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
from .api import Operation

PS = ParamSpec("PS")
RT = TypeVar("RT")


def params(value: QueryParamTypes, /):
    def decorator(operation: Operation[PS, RT], /) -> Operation[PS, RT]:
        spec: Optional[Specification] = api.get_specification(operation.func)

        if spec is None:
            raise Exception("Cannot configure callable without a spec")

        spec.request.params = QueryParams(value)

        return operation

    return decorator


def headers(value: HeaderTypes, /):
    def decorator(operation: Operation[PS, RT], /) -> Operation[PS, RT]:
        spec: Optional[Specification] = api.get_specification(operation.func)

        if spec is None:
            raise Exception("Cannot configure callable without a spec")

        spec.request.headers = Headers(value)

        return operation

    return decorator


def cookies(value: CookieTypes, /):
    def decorator(operation: Operation[PS, RT], /) -> Operation[PS, RT]:
        spec: Optional[Specification] = api.get_specification(operation.func)

        if spec is None:
            raise Exception("Cannot configure callable without a spec")

        spec.request.cookies = Cookies(value)

        return operation

    return decorator


def content(value: RequestContent, /):
    def decorator(operation: Operation[PS, RT], /) -> Operation[PS, RT]:
        spec: Optional[Specification] = api.get_specification(operation.func)

        if spec is None:
            raise Exception("Cannot configure callable without a spec")

        spec.request.content = value

        return operation

    return decorator


def data(value: RequestData, /):
    def decorator(operation: Operation[PS, RT], /) -> Operation[PS, RT]:
        spec: Optional[Specification] = api.get_specification(operation.func)

        if spec is None:
            raise Exception("Cannot configure callable without a spec")

        spec.request.data = value

        return operation

    return decorator


def files(value: RequestFiles, /):
    def decorator(operation: Operation[PS, RT], /) -> Operation[PS, RT]:
        spec: Optional[Specification] = api.get_specification(operation.func)

        if spec is None:
            raise Exception("Cannot configure callable without a spec")

        spec.request.files = value

        return operation

    return decorator


def json(value: JsonTypes, /):
    def decorator(operation: Operation[PS, RT], /) -> Operation[PS, RT]:
        spec: Optional[Specification] = api.get_specification(operation.func)

        if spec is None:
            raise Exception("Cannot configure callable without a spec")

        spec.request.json = value

        return operation

    return decorator


def timeout(value: TimeoutTypes, /):
    def decorator(operation: Operation[PS, RT], /) -> Operation[PS, RT]:
        spec: Optional[Specification] = api.get_specification(operation.func)

        if spec is None:
            raise Exception("Cannot configure callable without a spec")

        spec.request.timeout = Timeout(value)

        return operation

    return decorator
