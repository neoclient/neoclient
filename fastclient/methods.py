import abc
from types import FunctionType
from typing import Any, Callable, Optional, TypeVar

import annotate
from typing_extensions import ParamSpec

from . import api
from .enums import Annotation, HttpMethod
from .models import OperationSpecification
from .params import Path
from .api import Operation

PS = ParamSpec("PS")
RT = TypeVar("RT")


def request(
    method: str,
    endpoint: Optional[str] = None,
    /,
    *,
    response: Optional[Callable[..., Any]] = None,
) -> Callable[[Callable[PS, RT]], Operation[PS, RT]]:
    def decorator(func: Callable[PS, RT], /) -> Operation[PS, RT]:
        uri: str = (
            endpoint if endpoint is not None else Path.generate_alias(func.__name__)
        )

        spec: OperationSpecification = api.build_request_specification(
            func, method, uri, response=response
        )

        annotate.annotate(
            func,
            annotate.Annotation(
                key=Annotation.SPECIFICATION, value=spec, targets=(FunctionType,)
            ),
        )

        operation: Operation = Operation(func)

        return abc.abstractmethod(operation)

    return decorator


def put(
    endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    return request(HttpMethod.PUT.name, endpoint, response=response)


def get(
    endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    return request(HttpMethod.GET.name, endpoint, response=response)


def post(
    endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    return request(HttpMethod.POST.name, endpoint, response=response)


def head(
    endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    return request(HttpMethod.HEAD.name, endpoint, response=response)


def patch(
    endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    return request(HttpMethod.PATCH.name, endpoint, response=response)


def delete(
    endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    return request(HttpMethod.DELETE.name, endpoint, response=response)


def options(
    endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    return request(HttpMethod.OPTIONS.name, endpoint, response=response)
