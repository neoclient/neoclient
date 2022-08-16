from typing import Optional, TypeVar, Union
from .sentinels import Missing, MissingType
from . import params


T = TypeVar("T")


def Header(
    name: Optional[str] = None, *, default: Union[T, MissingType] = Missing
) -> params.Header[T]:
    return params.Header(name=name, default=default)


def Query(
    name: Optional[str] = None, *, default: Union[T, MissingType] = Missing
) -> params.Query[T]:
    return params.Query(name=name, default=default)


def Path(
    name: Optional[str] = None, *, default: Union[T, MissingType] = Missing
) -> params.Path[T]:
    return params.Path(name=name, default=default)


def Cookie(
    name: Optional[str] = None, *, default: Union[T, MissingType] = Missing
) -> params.Cookie[T]:
    return params.Cookie(name=name, default=default)
