import inspect
import string
from typing import Any, Callable, Dict, Optional, Set, Tuple

import parse


def get_path_params(url: str, /) -> Set[str]:
    path_params: Set[str] = set()

    field_name: Optional[str]
    for _, field_name, _, _ in string.Formatter().parse(url):
        if field_name is None:
            continue

        if not field_name.isidentifier():
            raise ValueError(f"Field name {field_name!r} is not a valid identifier")

        path_params.add(field_name)

    return path_params


def extract_path_params(url_format: str, url: str, /) -> Dict[str, Any]:
    parse_result: Optional[parse.Result] = parse.parse(url_format, url)

    if parse_result is None:
        raise ValueError(
            f"Failed to parse url {url!r} against format spec {url_format!r}"
        )

    return parse_result.named


def partially_format(string: str, /, **kwargs: Any) -> str:
    default_kwargs: Dict[str, str] = {
        path_param: f"{{{path_param}}}" for path_param in get_path_params(string)
    }

    return string.format(**{**default_kwargs, **kwargs})


def bind_arguments(
    func: Callable, args: Tuple[Any, ...], kwargs: Dict[str, Any]
) -> Dict[str, Any]:
    bound_arguments: inspect.BoundArguments = inspect.signature(func).bind(
        *args, **kwargs
    )

    bound_arguments.apply_defaults()

    return bound_arguments.arguments


def noop_consumer(_: Any, /) -> None:
    return None


def is_primitive(obj: Any, /) -> bool:
    return isinstance(obj, (str, int, float, bool, type(None)))
