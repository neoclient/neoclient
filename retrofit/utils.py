from typing import Set
import parse


def get_path_params(url: str, /) -> Set[str]:
    return set(parse.compile(url).named_fields)
