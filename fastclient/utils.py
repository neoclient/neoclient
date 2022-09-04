import string
from typing import Any, Dict, Optional, Set

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
        raise Exception(
            f"Failed to parse url {url!r} against format spec {url_format!r}"
        )

    return parse_result.named
