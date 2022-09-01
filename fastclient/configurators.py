from typing import Callable, Optional, TypeVar
from typing_extensions import ParamSpec
from . import api
from .models import Specification
from .types import HeadersType, TimeoutType
from httpx import Timeout, Headers

PS = ParamSpec("PS")
RT = TypeVar("RT")


def timeout(value: TimeoutType, /):
    def decorator(func: Callable[PS, RT], /) -> Callable[PS, RT]:
        spec: Optional[Specification] = api.get_specification(func)

        if spec is None:
            raise Exception("Cannot configure callable without a spec")

        spec.request.timeout = Timeout(value)

        return func

    return decorator


def headers(value: HeadersType, /):
    def decorator(func: Callable[PS, RT], /) -> Callable[PS, RT]:
        spec: Optional[Specification] = api.get_specification(func)

        if spec is None:
            raise Exception("Cannot configure callable without a spec")

        spec.request.headers = Headers(value)

        return func

    return decorator
