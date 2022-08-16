from typing import Optional, TypeVar, Union
from .sentinels import Missing, MissingType
from . import params


T = TypeVar("T")


def Header(
    name: Optional[str] = None, *, default: Union[T, MissingType] = Missing
) -> params.Header[T]:
    return params.Header(name=name, default=default)
