from dataclasses import dataclass
from typing import Any, Callable, Dict, TypeVar, Type
from typing_extensions import ParamSpec
import annotate

from .converters import Converter, IdentityConverter, IdentityResolver, Resolver
from .enums import FieldType, Annotation
from .models import FieldInfo, Specification, Query, Request, Info
from types import FunctionType
import urllib.parse
import inspect
import functools
from . import utils

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
    base_url: str
    resolver: Resolver = IdentityResolver()
    converter: Converter = IdentityConverter()

    def create(self, protocol: Type[T], /) -> T:
        specifications: Dict[str, Specification] = get_specifications(protocol)

        attributes: dict = {"__module__": protocol.__module__}

        func_name: str
        specification: Specification
        for func_name, specification in specifications.items():
            func: FunctionType = getattr(protocol, func_name)

            attributes[func_name] = self._method(specification, func)

        return type(protocol.__name__, (BaseService,), attributes)()

    def _url(self, endpoint: str, /) -> str:
        return urllib.parse.urljoin(self.base_url, endpoint)

    def _method(
        self, specification: Specification, method: Callable[PT, RT], /
    ) -> Callable[PT, RT]:
        signature: inspect.Signature = inspect.signature(method)

        @functools.wraps(method)
        @staticmethod
        def wrapper(*args: PT.args, **kwargs: PT.kwargs) -> Any:
            # TODO: Make `get_arguments` complain if the arguments don't conform to the spec
            arguments: Dict[str, Any] = utils.get_arguments(args, kwargs, signature)

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

            # TODO: Fix relationships between maps and single types
            maps: Dict[FieldType, FieldType] = {
                FieldType.HEADER_DICT: FieldType.HEADER,
                FieldType.QUERY_DICT: FieldType.QUERY,
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
                    destinations.setdefault(maps[field.type], {}).update(
                        arguments[parameter]
                    )

            return self.converter.convert(self.resolver.resolve(Request(
                method=specification.method,
                url=self._url(specification.endpoint).format(
                    **destinations.get(FieldType.PATH, {})
                ),
                params=destinations.get(FieldType.QUERY, {}),
                headers=destinations.get(FieldType.HEADER, {}),
            )))

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

        fields[parameter.name] = field

    return Specification(
        method=method,
        endpoint=endpoint,
        fields=fields,
    )
