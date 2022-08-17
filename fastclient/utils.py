from typing import Optional, Set
import string


def get_path_params(url: str, /) -> Set[str]:
    path_params: Set[str] = set()

    field_name: Optional[str]
    for _, field_name, _, _ in string.Formatter().parse(url):
        if field_name is None:
            continue

        if not field_name:
            raise ValueError("Field name is empty")

        if not field_name.isidentifier():
            raise ValueError(f"Field name {field_name!r} is not a valid identifier")

        path_params.add(field_name)

    return path_params
