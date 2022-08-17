from typing import Callable, Optional, TypeVar, Union
from .sentinels import Missing, MissingType
from . import params


T = TypeVar("T")


def Header(
    alias: Optional[str] = None,
    *,
    default: Union[T, MissingType] = Missing,
    default_factory: Union[Callable[[], T], MissingType] = Missing,
    required: bool = False
) -> params.Header[T]:
    return params.Header(
        alias=alias, default=default, default_factory=default_factory, required=required
    )

def Query(
    alias: Optional[str] = None,
    *,
    default: Union[T, MissingType] = Missing,
    default_factory: Union[Callable[[], T], MissingType] = Missing,
    required: bool = False
) -> params.Query[T]:
    return params.Query(
        alias=alias, default=default, default_factory=default_factory, required=required
    )

def Path(
    alias: Optional[str] = None,
    *,
    default: Union[T, MissingType] = Missing,
    default_factory: Union[Callable[[], T], MissingType] = Missing,
    required: bool = False
) -> params.Path[T]:
    return params.Path(
        alias=alias, default=default, default_factory=default_factory, required=required
    )

def Cookie(
    alias: Optional[str] = None,
    *,
    default: Union[T, MissingType] = Missing,
    default_factory: Union[Callable[[], T], MissingType] = Missing,
    required: bool = False
) -> params.Cookie[T]:
    return params.Cookie(
        alias=alias, default=default, default_factory=default_factory, required=required
    )

def Body(
    alias: Optional[str] = None,
    *,
    default: Union[T, MissingType] = Missing,
    default_factory: Union[Callable[[], T], MissingType] = Missing,
    required: bool = False
) -> params.Body[T]:
    return params.Body(
        alias=alias, default=default, default_factory=default_factory, required=required
    )


def Headers() -> params.Headers:
    return params.Headers()


def Queries() -> params.Queries:
    return params.Queries()


def Cookies() -> params.Cookies:
    return params.Cookies()
