from typing import Callable, Optional, TypeVar, Union
from .sentinels import Missing, MissingType
from . import params


T = TypeVar("T")


def Header(
    alias: Optional[str] = None, *, default: Union[T, MissingType] = Missing
) -> params.Header[T]:
    return params.Header(alias=alias, default=default)


def Query(
    alias: Optional[str] = None,
    *,
    default: Union[T, MissingType] = Missing,
    required: bool = False
) -> params.Query[T]:
    return params.Query(alias=alias, default=default, required=required)


def Path(
    alias: Optional[str] = None, *, default: Union[T, MissingType] = Missing
) -> params.Path[T]:
    return params.Path(alias=alias, default=default)


def Cookie(
    alias: Optional[str] = None, *, default: Union[T, MissingType] = Missing
) -> params.Cookie[T]:
    return params.Cookie(alias=alias, default=default)


def Body(
    default: Union[T, MissingType] = Missing,
    default_factory: Union[Callable[[], T], MissingType] = Missing,
) -> params.Body:
    return params.Body(default=default, default_factory=default_factory)


def Headers() -> params.Headers:
    return params.Headers()


def Queries() -> params.Queries:
    return params.Queries()


def Cookies() -> params.Cookies:
    return params.Cookies()
