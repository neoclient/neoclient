from types import FunctionType
from typing import Any, Callable, Dict, Optional, Union

from .models import Specification
from .enums import Annotation, ParamType, HttpMethod
from . import api
import inspect
import annotate


def request(
    method: str, endpoint: Optional[str] = None, /
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any], /) -> Callable[..., Any]:
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
            annotate.Annotation(
                Annotation.SPECIFICATION, spec, targets=(FunctionType,)
            ),
        )

        return func

    return decorator


def method(method: HttpMethod, /) -> Callable:
    def proxy(obj: Union[None, str, FunctionType], /):
        if isinstance(obj, FunctionType):
            return request(method.name)(obj)

        return request(method.name, obj)

    return proxy


put = method(HttpMethod.PUT)
get = method(HttpMethod.GET)
post = method(HttpMethod.POST)
head = method(HttpMethod.HEAD)
patch = method(HttpMethod.PATCH)
delete = method(HttpMethod.DELETE)
options = method(HttpMethod.OPTIONS)


def static(
    field_type: ParamType, data: Dict[str, Any]
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any], /) -> Callable[..., Any]:
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
