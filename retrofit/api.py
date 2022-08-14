from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TypeVar, Type, Union
from typing_extensions import ParamSpec
import annotate
from .enums import FieldType, HttpMethod, Annotation
from .models import FieldInfo, RequestSpecification, Query, Request, Info
from types import FunctionType
import urllib.parse
import inspect
import functools

T = TypeVar("T")

PT = ParamSpec("PT")
RT = TypeVar("RT")


def get_arguments(
    args: Any, kwargs: Any, signature: inspect.Signature
) -> Dict[str, Any]:
    positional_parameters: List[inspect.Parameter] = list(
        signature.parameters.values()
    )[: len(args)]

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

            attributes[member_name] = functools.wraps(member)(
                self._method(spec, member)
            )

        return type(protocol.__name__, (object,), attributes)()

    def _url(self, endpoint: str, /) -> str:
        return urllib.parse.urljoin(self.base_url, endpoint)

    def _method(
        self, specification: RequestSpecification, method: Callable[PT, RT], /
    ) -> Callable[PT, RT]:
        signature: inspect.Signature = inspect.signature(method)

        def wrapper(*args: PT.args, **kwargs: PT.kwargs) -> Any:
            # TODO: Make `get_arguments` complain if the arguments don't conform to the spec
            arguments: Dict[str, Any] = get_arguments(args, kwargs, signature)

            # omit_arguments: Set[str] = set()

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

                # Consciously choose to omit field with `None` value as it's likely not wanted
                # if field.default is None:
                #     omit_arguments.add(argument_name)

                arguments[argument_name] = field.default

            # print(arguments)

            # argument: str
            # for argument in omit_arguments:
            #     arguments.pop(argument)

            # print(arguments)

            sources: Dict[FieldType, Dict[str, Any]] = {
                FieldType.QUERY: specification.params,
                FieldType.PATH: specification.path_params,
                FieldType.HEADER: specification.headers,
            }

            destinations: Dict[FieldType, Dict[str, Info]] = {}

            field_type: FieldType
            data: Dict[str, Info]
            for field_type, data in sources.items():
                destinations[field_type] = {}

                parameter: str
                field: Info
                for parameter, field in data.items():
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

                        destinations[field_type][field_name] = value
                    else:
                        destinations[field_type].update(arguments[parameter])

            return Request(
                method=specification.method,
                url=self._url(specification.endpoint).format(
                    **destinations[FieldType.PATH]
                ),
                params=destinations[FieldType.QUERY],
                headers=destinations[FieldType.HEADER],
            )

        return wrapper


def build_request_specification(
    method: str, endpoint: str, signature: inspect.Signature
) -> RequestSpecification:
    if not signature.parameters:
        raise ValueError(
            "Signature expects no parameters. Should expect at least `self`"
        )

    # Ignore first parameter, as it should be `self`
    parameters: List[inspect.Parameter] = list(signature.parameters.values())[1:]

    destinations: Dict[FieldType, Dict[str, Info]] = {
        field_type: {} for field_type in FieldType
    }

    parameter: inspect.Parameter
    for parameter in parameters:
        default: Any = parameter.default

        # Assume it's a `Query` field if the type is not known
        field: Info = (
            default
            if isinstance(default, Info)
            else Query(name=parameter.name, default=default)
        )

        destinations[field.type][parameter.name] = field

    return RequestSpecification(
        method=method,
        endpoint=endpoint,
        params={**destinations[FieldType.QUERY_DICT], **destinations[FieldType.QUERY]},
        path_params=destinations[FieldType.PATH],
        headers={
            **destinations[FieldType.HEADER_DICT],
            **destinations[FieldType.HEADER],
        },
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

        spec: RequestSpecification = build_request_specification(
            method, uri, inspect.signature(func)
        )

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
