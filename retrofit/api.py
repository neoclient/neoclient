from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Type, Union
import annotate
from .enums import FieldType, HttpMethod, Annotation
from .models import FieldInfo, RequestSpecification, Query, Request
from types import FunctionType
import urllib.parse
import inspect

T = TypeVar("T")


def get_arguments(args: Any, kwargs: Any, signature: inspect.Signature) -> Dict[str, Any]:
    positional_parameters: List[inspect.Parameter] = list(signature.parameters.values())[: len(args)]

    positional: Dict[str, Any] = {
        parameter.name: arg for arg, parameter in zip(args, positional_parameters)
    }

    defaults: Dict[str, Any] = {
        parameter.name: parameter.default
        for parameter in signature.parameters.values()
        if parameter.default is not parameter.empty
    }

    return {**defaults, **positional, **kwargs}


@dataclass
class Retrofit:
    base_url: str

    def create(self, protocol: Type[T], /) -> T:
        members: List[Tuple[str, Any]] = inspect.getmembers(protocol)

        attributes: dict = {}

        member_name: str
        member: Any
        for member_name, member in members:
            annotations: dict = annotate.get_annotations(member)

            if Annotation.SPECIFICATION not in annotations:
                continue

            spec: RequestSpecification = annotations[Annotation.SPECIFICATION]

            attributes[member_name] = self._method(spec, member)

        return type(protocol.__name__, (object,), attributes)()

    def _url(self, endpoint: str, /) -> str:
        return urllib.parse.urljoin(self.base_url, endpoint)

    def _method(
        self, specification: RequestSpecification, method: FunctionType, /
    ) -> Callable:
        signature: inspect.Signature = inspect.signature(method)

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            arguments: Dict[str, Any] = get_arguments(args, kwargs, signature)

            sources: Dict[FieldType, Dict[str, Any]] = {
                FieldType.QUERY: specification.params,
                FieldType.PATH: specification.path_params,
                FieldType.HEADER: specification.headers
            }

            destinations: Dict[FieldType, Dict[str, FieldInfo]] = {
                field_type: {
                    parameter: arguments[field.name]
                    for parameter, field in data.items()
                }
                for field_type, data in sources.items()
            }

            return Request(
                method=specification.method,
                url=self._url(specification.endpoint).format(**destinations[FieldType.PATH]),
                params=destinations[FieldType.QUERY],
                headers=destinations[FieldType.HEADER]
            )

        return wrapper


def build_request_specification(method: str, endpoint: str, signature: inspect.Signature) -> RequestSpecification:
    # Ignore first parameter, as it should be `self`
    parameters: List[inspect.Parameter] = list(signature.parameters.values())[1:]

    destinations: Dict[FieldType, Dict[str, FieldInfo]] = {
        FieldType.QUERY: {},
        FieldType.PATH: {},
        FieldType.HEADER: {}
    }

    parameter: inspect.Parameter
    for parameter in parameters:
        default: Any = parameter.default

        # Assume it's a `Query` field if the type is not known
        field: FieldInfo = (
            default
            if isinstance(default, FieldInfo)
            else Query(name=parameter.name, default=default)
        )

        destinations[field.type][parameter.name] = field

    return RequestSpecification(
        method=method,
        endpoint=endpoint,
        params=destinations[FieldType.QUERY],
        path_params=destinations[FieldType.PATH],
        headers=destinations[FieldType.HEADER],
    )


def request(method: str, endpoint: Optional[str] = None, /):
    def decorate(func: FunctionType, /) -> FunctionType:
        uri: str = endpoint if endpoint is not None else func.__name__

        spec: RequestSpecification = build_request_specification(method, uri, inspect.signature(func))

        annotate.annotate(
            func,
            annotate.Annotation(Annotation.SPECIFICATION, spec),
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
