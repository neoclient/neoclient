from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Tuple, TypeVar, Type
import annotate
from .enums import HttpMethod, Annotation
from .models import RequestSpecification, Path, Param, Request, Header
from types import MethodType
import urllib.parse
import inspect

T = TypeVar("T")

def get_arguments(args, kwargs, signature):
    positional_parameters = list(signature.parameters.values())[:len(args)]

    positional = {
        parameter.name: arg
        for arg, parameter in zip(args, positional_parameters)
    }

    defaults = {
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

    def _method(self, specification: RequestSpecification, method: MethodType, /) -> Callable:
        signature = inspect.signature(method)

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            arguments = get_arguments(args, kwargs, signature)

            params = {
                field: arguments[param.name]
                for field, param in specification.params.items()
            }
            
            path_params = {
                field: arguments[path.name]
                for field, path in specification.path_params.items()
            }

            headers = {
                field: arguments[header.name]
                for field, header in specification.headers.items()
            }

            return Request(
                method=specification.method,
                url=self._url(specification.endpoint).format(**path_params),
                params=params,
                headers=headers,
            )

        return wrapper

def build_spec(verb: str, endpoint: str, method: MethodType) -> RequestSpecification:
    signature = inspect.signature(method)

    parameters = list(signature.parameters.values())[1:]

    params: Dict[str, Param] = {}
    headers: Dict[str, Header] = {}
    path_params: Dict[str, Path] = {}

    for parameter in parameters:
        default = parameter.default

        if isinstance(default, Path):
            path: Path = default

            path_params[parameter.name] = path
        elif isinstance(default, Param):
            param: Param = default

            params[parameter.name] = param
        elif isinstance(default, Header):
            header: Header = default

            headers[header.name] = header

    return RequestSpecification(method=verb, endpoint=endpoint, params=params, path_params=path_params, headers=headers)


def method(verb: HttpMethod, /):
    def proxy(endpoint: str, /):
        def decorate(method: MethodType, /):
            spec: RequestSpecification = build_spec(verb.value, endpoint, method)

            annotate.annotate(
                method,
                annotate.Annotation(
                    Annotation.SPECIFICATION, spec
                ),
            )

            return method

        return decorate

    return proxy

put = method(HttpMethod.PUT)
get = method(HttpMethod.GET)
post = method(HttpMethod.POST)
head = method(HttpMethod.HEAD)
patch = method(HttpMethod.PATCH)
delete = method(HttpMethod.DELETE)
options = method(HttpMethod.OPTIONS)