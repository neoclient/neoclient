from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Set, TypeVar, Type
from typing_extensions import ParamSpec
import annotate

from .converters import Converter, HttpxJsonConverter, HttpxResolver, Resolver
from .enums import FieldType, Annotation
from .models import FieldDictInfo, FieldInfo, Path, Specification, Query, Request, Info
from types import FunctionType
import inspect
import functools
import furl
from arguments import Arguments
import parse

T = TypeVar("T")

PT = ParamSpec("PT")
RT = TypeVar("RT")


def get_specifications(cls: type, /) -> Dict[str, Specification]:
    return {
        member_name: annotate.get_annotations(member)[Annotation.SPECIFICATION]
        for member_name, member in inspect.getmembers(cls)
        if isinstance(member, FunctionType)
        and Annotation.SPECIFICATION in annotate.get_annotations(member)
    }


class BaseService:
    def __repr__(self) -> str:
        return f"<{type(self).__name__}()>"


@dataclass
class Retrofit:
    base_url: Optional[str] = None
    resolver: Resolver = HttpxResolver()
    converter: Converter = HttpxJsonConverter()

    def create(self, protocol: Type[T], /) -> T:
        specifications: Dict[str, Specification] = get_specifications(protocol)

        attributes: dict = {"__module__": protocol.__module__}

        func_name: str
        specification: Specification
        for func_name, specification in specifications.items():
            func: FunctionType = getattr(protocol, func_name)

            # Validate endpoint is a fully qualified url if no base url
            if (
                self.base_url is None or not furl.has_netloc(self.base_url)
            ) and not furl.has_netloc(specification.endpoint):
                raise Exception(
                    f"Cannot construct fully-qualified URL from: base_url={self.base_url!r}, endpoint={specification.endpoint!r}"
                )

            attributes[func_name] = self._method(specification, func)

        return type(protocol.__name__, (BaseService,), attributes)()

    def _url(self, endpoint: str, /) -> str:
        if furl.has_netloc(endpoint):
            return endpoint

        if self.base_url is None or not furl.has_netloc(self.base_url):
            raise Exception(
                f"Cannot construct fully-qualified URL from: base_url={self.base_url!r}, endpoint={endpoint!r}"
            )

        return furl.urljoin(self.base_url, endpoint)

    def _method(
        self, specification: Specification, method: Callable[PT, RT], /
    ) -> Callable[PT, RT]:
        @functools.wraps(method)
        @staticmethod
        def wrapper(*args: PT.args, **kwargs: PT.kwargs) -> Any:
            arguments: Dict[str, Any] = Arguments(*args, **kwargs).bind(method).asdict()

            argument_name: str
            argument: Any
            for argument_name, argument in arguments.items():
                if not isinstance(argument, Info):
                    continue

                if not argument.has_default():
                    raise ValueError(
                        f"{method.__name__}() missing argument: {argument_name!r}"
                    )

                arguments[argument_name] = argument.default

            destinations: Dict[FieldType, Dict[str, Info]] = {}

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
                elif isinstance(field, FieldDictInfo):
                    destinations.setdefault(field.type, {}).update(arguments[parameter])

            return self.converter.convert(
                self.resolver.resolve(
                    Request(
                        method=specification.method,
                        url=self._url(specification.endpoint).format(
                            **destinations.get(FieldType.PATH, {})
                        ),
                        params=destinations.get(FieldType.QUERY, {}),
                        headers=destinations.get(FieldType.HEADER, {}),
                    )
                )
            )

        return wrapper


def build_request_specification(
    method: str, endpoint: str, signature: inspect.Signature
) -> Specification:
    fields: Dict[str, Info] = {}

    parameter: inspect.Parameter
    for parameter in signature.parameters.values():
        default: Any = parameter.default

        # Assume it's a `Query` field if the type is not known
        field: Info = (
            default
            if isinstance(default, Info)
            else Query(name=parameter.name, default=default)
        )

        if isinstance(field, FieldInfo) and field.name is None:
            field.name = field.generate_name(parameter.name)

        fields[parameter.name] = field

    expected_path_params: Set[str] = set(parse.compile(endpoint).named_fields)
    actual_path_params: Set[str] = {
        field.name for field in fields.values() if isinstance(field, Path)
    }

    # Validate that only expected path params provided
    if expected_path_params != actual_path_params:
        raise ValueError(
            f"Incompatible path params. Got: {actual_path_params}, expected: {expected_path_params}"
        )

    return Specification(
        method=method,
        endpoint=endpoint,
        fields=fields,
    )
