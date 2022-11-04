import inspect
import string
from typing import (
    Any,
    Callable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Set,
    Tuple,
)


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

    args: List[Any] = []
    kwargs: MutableMapping[str, Any] = {}

    parameter: inspect.Parameter
    for parameter in parameters.values():
        argument: Any = arguments[parameter.name]

        if parameter.kind is inspect.Parameter.POSITIONAL_ONLY:
            args.append(argument)
        elif parameter.kind in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        ):
            kwargs[parameter.name] = argument
        elif parameter.kind is inspect.Parameter.VAR_POSITIONAL:
            args.extend(argument)
        elif parameter.kind is inspect.Parameter.VAR_KEYWORD:
            kwargs.update(argument)
        else:
            raise Exception(f"Unknown parameter kind: {parameter.kind}")

    return (tuple(args), kwargs)
