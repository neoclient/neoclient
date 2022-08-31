import abc
from types import FunctionType
from typing import Any, Callable, Dict, Optional, TypeVar

import annotate
from typing_extensions import ParamSpec

from . import api
from .enums import Annotation, HttpMethod, ParamType
from .models import Specification
from .params import Path

PS = ParamSpec("PS")
RT = TypeVar("RT")


def request(
    method: str,
    endpoint: Optional[str] = None,
    /,
    *,
    response: Optional[Callable[..., Any]] = None,
) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    def decorator(func: Callable[PS, RT], /) -> Callable[PS, RT]:
        uri: str = (
            endpoint if endpoint is not None else Path.generate_alias(func.__name__)
        )

        spec: Specification = api.build_request_specification(
            func, method, uri, response=response
        )

        annotate.annotate(
            func,
            annotate.Annotation(
                key=Annotation.SPECIFICATION, value=spec, targets=(FunctionType,)
            ),
        )

        return abc.abstractmethod(func)

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


def static(
    field_type: ParamType, data: Dict[str, Any]
) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    def decorator(func: Callable[PS, RT], /) -> Callable[PS, RT]:
        specification: Optional[Specification] = api.get_specification(func)

        if specification is None:
            raise Exception(
                f"{func!r} has no specification. Cannot add static {field_type.name} fields"
            )

        destinations: Dict[ParamType, Dict[str, Any]] = {
            ParamType.QUERY: specification.request.params,
            ParamType.HEADER: specification.request.headers,
        }

        destinations[field_type].update(data)

        return func

    return decorator


def headers(data: Dict[str, Any], /) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    return static(ParamType.HEADER, data)


def query_params(
    data: Dict[str, Any], /
) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    return static(ParamType.QUERY, data)
