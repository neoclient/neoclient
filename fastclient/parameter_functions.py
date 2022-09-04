from typing import Callable, Optional, TypeVar, Union

from param.sentinels import Missing, MissingType

from . import parameters

T = TypeVar("T")


def Header(
    alias: Optional[str] = None,
    *,
    default: Union[T, MissingType] = Missing,
    default_factory: Union[Callable[[], T], MissingType] = Missing,
    required: bool = False,
) -> parameters.Header[T]:
    return parameters.Header(
        alias=alias, default=default, default_factory=default_factory, required=required
    )


def Query(
    alias: Optional[str] = None,
    *,
    default: Union[T, MissingType] = Missing,
    default_factory: Union[Callable[[], T], MissingType] = Missing,
    required: bool = False,
) -> parameters.Query[T]:
    return parameters.Query(
        alias=alias, default=default, default_factory=default_factory, required=required
    )


def Path(
    alias: Optional[str] = None,
    *,
    default: Union[T, MissingType] = Missing,
    default_factory: Union[Callable[[], T], MissingType] = Missing,
    required: bool = False,
) -> parameters.Path[T]:
    return parameters.Path(
        alias=alias, default=default, default_factory=default_factory, required=required
    )


def Cookie(
    alias: Optional[str] = None,
    *,
    default: Union[T, MissingType] = Missing,
    default_factory: Union[Callable[[], T], MissingType] = Missing,
    required: bool = False,
) -> parameters.Cookie[T]:
    return parameters.Cookie(
        alias=alias, default=default, default_factory=default_factory, required=required
    )


def Body(
    alias: Optional[str] = None,
    *,
    default: Union[T, MissingType] = Missing,
    default_factory: Union[Callable[[], T], MissingType] = Missing,
    required: bool = False,
) -> parameters.Body[T]:
    return parameters.Body(
        alias=alias, default=default, default_factory=default_factory, required=required
    )


def Headers() -> parameters.Headers:
    return parameters.Headers()


def Queries() -> parameters.Queries:
    return parameters.Queries()


def Cookies() -> parameters.Cookies:
    return parameters.Cookies()


def Depends(
    dependency: Optional[Callable[..., T]] = None, /, *, use_cache: bool = True
) -> parameters.Depends[T]:
    return parameters.Depends(dependency, use_cache=use_cache)


def Promise(promised_type: Optional[T] = None, /) -> parameters.Promise[T]:
    return parameters.Promise(promised_type)
