from types import FunctionType
from typing import Any, Callable, Dict, Optional, TypeVar
from typing_extensions import ParamSpec

from .models import Specification
from .enums import Annotation, ParamType, HttpMethod
from . import api
import inspect
import annotate
from .params import Path

PS = ParamSpec("PS")
RT = TypeVar("RT")


def request(
    method: str, endpoint: Optional[str] = None, /
) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    def decorator(func: Callable[PS, RT], /) -> Callable[PS, RT]:
        uri: str = (
            endpoint
            if endpoint is not None
            else Path.generate_name(func.__name__)
        )

        spec: Specification = api.build_request_specification(
            method, uri, inspect.signature(func)
        )

        annotate.annotate(
            func,
            annotate.Annotation(
                Annotation.SPECIFICATION, spec, targets=(FunctionType,)
            ),
        )

        return func

    return decorator


def _method(method: HttpMethod, /) -> Callable[[str], Callable[[Callable[PS, RT]], Callable[PS, RT]]]:
    def proxy(url: str, /) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
        return request(method.name, url)

    return proxy


put: Callable[[str], Callable[[Callable[PS, RT]], Callable[PS, RT]]] = _method(HttpMethod.PUT)
get: Callable[[str], Callable[[Callable[PS, RT]], Callable[PS, RT]]] = _method(HttpMethod.GET)
post: Callable[[str], Callable[[Callable[PS, RT]], Callable[PS, RT]]] = _method(HttpMethod.POST)
head: Callable[[str], Callable[[Callable[PS, RT]], Callable[PS, RT]]] = _method(HttpMethod.HEAD)
patch: Callable[[str], Callable[[Callable[PS, RT]], Callable[PS, RT]]] = _method(HttpMethod.PATCH)
delete: Callable[[str], Callable[[Callable[PS, RT]], Callable[PS, RT]]] = _method(HttpMethod.DELETE)
options: Callable[[str], Callable[[Callable[PS, RT]], Callable[PS, RT]]] = _method(HttpMethod.OPTIONS)


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
            ParamType.QUERY: specification.params,
            ParamType.HEADER: specification.headers,
        }

        destinations[field_type].update(data)

        return func

    return decorator


def _static_for_field(field_type: ParamType):
    def outer(data: Dict[str, Any], /):
        return static(field_type, data)

    return outer


headers = _static_for_field(ParamType.HEADER)
query_params = _static_for_field(ParamType.QUERY)
