import inspect
import string
from types import FunctionType, MethodType
from typing import (
    Any,
    Callable,
    Mapping,
    MutableMapping,
    MutableSequence,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from pydantic import BaseConfig, BaseModel, create_model
from pydantic.fields import FieldInfo, Undefined
from pydantic.typing import display_as_type

from .enums import MethodKind

__all__: Sequence[str] = (
    "parse_format_string",
    "bind_arguments",
    "is_primitive",
    "unpack_arguments",
    "get_default",
    "has_default",
    "get_method_kind",
    "parse_obj_as",
)

T = TypeVar("T")


def parse_format_string(format_string: str, /) -> Set[str]:
    """
    Extracts a set of field names from `format_string`

    Example:
        >>> parse_format_string("foo {bar}")
        {"bar"}
    """

    path_params: Set[str] = set()

    field_name: Optional[str]
    for _, field_name, _, _ in string.Formatter().parse(format_string):
        if field_name is None:
            continue

        if not field_name.isidentifier():
            raise ValueError(f"Field name {field_name!r} is not a valid identifier")

        path_params.add(field_name)

    return path_params


def bind_arguments(
    func: Callable, /, args: Tuple[Any, ...], kwargs: Mapping[str, Any]
) -> Mapping[str, Any]:
    bound_arguments: inspect.BoundArguments = inspect.signature(func).bind(
        *args, **kwargs
    )

    bound_arguments.apply_defaults()

    return bound_arguments.arguments


def is_primitive(obj: Any, /) -> bool:
    return isinstance(obj, (str, int, float, bool, type(None)))


def unpack_arguments(
    func: Callable, arguments: Mapping[str, Any]
) -> Tuple[Tuple[Any, ...], Mapping[str, Any]]:
    parameters: Mapping[str, inspect.Parameter] = inspect.signature(func).parameters

    args: MutableSequence[Any] = []
    kwargs: MutableMapping[str, Any] = {}

    parameter: inspect.Parameter
    for parameter in parameters.values():
        if parameter.name not in arguments:
            raise ValueError(f"Missing argument for parameter {parameter.name!r}")

        argument: Any = arguments[parameter.name]

        if parameter.kind == inspect.Parameter.POSITIONAL_ONLY:
            args.append(argument)
        elif parameter.kind in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        ):
            kwargs[parameter.name] = argument
        elif parameter.kind == inspect.Parameter.VAR_POSITIONAL:
            args.extend(argument)
        else:
            assert parameter.kind == inspect.Parameter.VAR_KEYWORD

            kwargs.update(argument)

    return (tuple(args), kwargs)


def get_default(field_info: FieldInfo, /) -> Any:
    if field_info.default_factory is not None:
        return field_info.default_factory()
    else:
        return field_info.default


def has_default(field_info: FieldInfo, /) -> bool:
    return field_info.default is not Undefined or field_info.default_factory is not None


def get_method_kind(method: Union[FunctionType, MethodType, Callable], /) -> MethodKind:
    if isinstance(method, MethodType):
        if isinstance(method.__self__, type):
            return MethodKind.CLASS_METHOD
        else:
            return MethodKind.METHOD
    elif isinstance(method, FunctionType):
        return MethodKind.STATIC_METHOD
    else:
        raise ValueError(
            f"Method {method!r} is not a function or method, cannot determine its kind"
        )


def parse_obj_as(type_: Type[T], obj: Any) -> T:
    parsing_type_name: str = f"ParsingModel[{display_as_type(type_)}]"

    class Config(BaseConfig):
        arbitrary_types_allowed: bool = True

    model_cls: Type[BaseModel] = create_model(
        parsing_type_name,
        __config__=Config,
        __root__=(type_, ...),
    )

    model: BaseModel = model_cls(__root__=obj)

    return getattr(model, "__root__")
