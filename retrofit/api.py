from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Protocol, Set, Tuple, TypeVar, Type, Union
from typing_extensions import ParamSpec
import annotate
from .enums import FieldType, HttpMethod, Annotation
from .models import FieldInfo, Specification, Query, Request, Info
from types import FunctionType
import urllib.parse
import inspect
import functools
from . import utils

T = TypeVar("T")

PT = ParamSpec("PT")
RT = TypeVar("RT")

def get_operations(protocol: Protocol, /) -> Dict[str, FunctionType]:
    return {
        member_name: member
        for member_name, member in inspect.getmembers(protocol)
        if Annotation.SPECIFICATION in annotate.get_annotations(member)
    }

@dataclass
class Retrofit:
    base_url: str

    def create(self, protocol: Type[T], /) -> T:
        operations: Dict[str, FunctionType] = get_operations(protocol)

        attributes: dict = {"__module__": protocol.__module__}

        func_name: str
        func: FunctionType
        for func_name, func in operations.items():
            specification: Specification = annotate.get_annotations(func)[Annotation.SPECIFICATION]

            attributes[func_name] = self._method(specification, func)

        return type(protocol.__name__, (object,), attributes)()

    def _url(self, endpoint: str, /) -> str:
        return urllib.parse.urljoin(self.base_url, endpoint)

    def _method(
        self, specification: Specification, method: Callable[PT, RT], /
    ) -> Callable[PT, RT]:
        signature: inspect.Signature = inspect.signature(method)

        @functools.wraps(method)
        def wrapper(*args: PT.args, **kwargs: PT.kwargs) -> Any:
            # TODO: Make `get_arguments` complain if the arguments don't conform to the spec
            arguments: Dict[str, Any] = utils.get_arguments(args, kwargs, signature)

            argument_name: str
            argument: Any
            for argument_name, argument in arguments.items():
                if not isinstance(argument, Info):
                    continue

                field: Info = argument

                if not field.has_default():
                    raise ValueError(
                        f"{method.__name__}() missing argument: {argument_name!r}"
                    )

                arguments[argument_name] = field.default

            destinations: Dict[FieldType, Dict[str, Info]] = {}

            # TODO: Fix relationships between maps and single types
            maps: Dict[FieldType, FieldType] = {
                FieldType.HEADER_DICT: FieldType.HEADER,
                FieldType.QUERY_DICT: FieldType.QUERY
            }

            parameter: str
            field: Info
            for parameter, field in specification.fields.items():
                if isinstance(field, FieldInfo):
                    field_name: str = (
                        field.name
                        if field.name is not None
                        else field.generate_name(parameter)
                    )
                    value: Any = arguments[parameter]

                    # Consciously choose to omit field with `None` value as it's likely not wanted
                    if value is None:
                        continue

                    destinations.setdefault(field.type, {})[field_name] = value
                else:
                    destinations.setdefault(maps[field.type], {}).update(arguments[parameter])

            return Request(
                method=specification.method,
                url=self._url(specification.endpoint).format(
                    **destinations.get(FieldType.PATH, {})
                ),
                params=destinations.get(FieldType.QUERY, {}),
                headers=destinations.get(FieldType.HEADER, {}),
            )

        return wrapper


def build_request_specification(
    method: str, endpoint: str, signature: inspect.Signature
) -> Specification:
    if not signature.parameters:
        raise ValueError(
            "Signature expects no parameters. Should expect at least `self`"
        )

    # Ignore first parameter, as it should be `self`
    parameters: List[inspect.Parameter] = list(signature.parameters.values())[1:]

    fields: Dict[str, Info] = {}

    parameter: inspect.Parameter
    for parameter in parameters:
        default: Any = parameter.default

        # Assume it's a `Query` field if the type is not known
        field: Info = (
            default
            if isinstance(default, Info)
            else Query(name=parameter.name, default=default)
        )

        fields[parameter.name] = field

    return Specification(
        method=method,
        endpoint=endpoint,
        fields=fields,
    )


def request(
    method: str, endpoint: Optional[str] = None, /
) -> Callable[[FunctionType], FunctionType]:
    def decorate(func: FunctionType, /) -> FunctionType:
        uri: str = (
            endpoint
            if endpoint is not None
            else func.__name__.lower().replace("_", "-")
        )

        spec: Specification = build_request_specification(
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
