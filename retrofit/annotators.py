from types import FunctionType
from typing import Callable, Optional, Union

from .models import Specification
from .enums import Annotation, HttpMethod
from . import api
import inspect
import annotate


def request(
    method: str, endpoint: Optional[str] = None, /
) -> Callable[[FunctionType], FunctionType]:
    def decorate(func: FunctionType, /) -> FunctionType:
        uri: str = (
            endpoint
            if endpoint is not None
            else func.__name__.lower().replace("_", "-")
        )

        spec: Specification = api.build_request_specification(
            method, uri, inspect.signature(func)
        )

        annotate.annotate(
            func,
            annotate.Annotation(Annotation.SPECIFICATION, spec, targets=(FunctionType,)),
        )

        return func

    return decorate


def method(method: HttpMethod, /) -> Callable:
    def proxy(obj: Union[None, str, FunctionType], /):
        if isinstance(obj, FunctionType):
            return request(method.value)(obj)

        return request(method.value, obj)

    return proxy


put = method(HttpMethod.PUT)
get = method(HttpMethod.GET)
post = method(HttpMethod.POST)
head = method(HttpMethod.HEAD)
patch = method(HttpMethod.PATCH)
delete = method(HttpMethod.DELETE)
options = method(HttpMethod.OPTIONS)
