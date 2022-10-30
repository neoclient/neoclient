from typing import Any, Callable, Optional, Type, Union

from httpx import Request, Response
from param.typing import Supplier
from pydantic.fields import Undefined, UndefinedType

from .parameters import (
    BodyParameter,
    CookieParameter,
    CookiesParameter,
    DependencyParameter,
    HeaderParameter,
    HeadersParameter,
    PathParameter,
    PathsParameter,
    PromiseParameter,
    QueriesParameter,
    QueryParameter,
)


def Query(
    alias: Optional[str] = None,
    *,
    default: Union[Any, UndefinedType] = Undefined,
    default_factory: Optional[Supplier[Any]] = None,
) -> QueryParameter:
    return QueryParameter(alias=alias, default=default, default_factory=default_factory)


def Header(
    alias: Optional[str] = None,
    *,
    default: Union[Any, UndefinedType] = Undefined,
    default_factory: Optional[Supplier[Any]] = None,
) -> HeaderParameter:
    return HeaderParameter(
        alias=alias, default=default, default_factory=default_factory
    )


def Cookie(
    alias: Optional[str] = None,
    *,
    default: Union[Any, UndefinedType] = Undefined,
    default_factory: Optional[Supplier[Any]] = None,
) -> CookieParameter:
    return CookieParameter(
        alias=alias, default=default, default_factory=default_factory
    )


def Path(
    alias: Optional[str] = None,
    *,
    default: Union[Any, UndefinedType] = Undefined,
    default_factory: Optional[Supplier[Any]] = None,
) -> PathParameter:
    return PathParameter(alias=alias, default=default, default_factory=default_factory)


def Queries(
    *,
    default: Union[Any, UndefinedType] = Undefined,
    default_factory: Optional[Supplier[Any]] = None,
) -> QueriesParameter:
    return QueriesParameter(
        default=default,
        default_factory=default_factory,
    )


def Headers(
    *,
    default: Union[Any, UndefinedType] = Undefined,
    default_factory: Optional[Supplier[Any]] = None,
) -> HeadersParameter:
    return HeadersParameter(
        default=default,
        default_factory=default_factory,
    )


def Cookies(
    *,
    default: Union[Any, UndefinedType] = Undefined,
    default_factory: Optional[Supplier[Any]] = None,
) -> CookiesParameter:
    return CookiesParameter(
        default=default,
        default_factory=default_factory,
    )


def Paths(
    *,
    default: Union[Any, UndefinedType] = Undefined,
    default_factory: Optional[Supplier[Any]] = None,
) -> PathsParameter:
    return PathsParameter(
        default=default,
        default_factory=default_factory,
    )


def Body(
    alias: Optional[str] = None,
    *,
    default: Union[Any, UndefinedType] = Undefined,
    default_factory: Optional[Supplier[Any]] = None,
    embed: bool = False,
) -> BodyParameter:
    return BodyParameter(
        alias=alias,
        default=default,
        default_factory=default_factory,
        embed=embed,
    )


def Depends(
    dependency: Optional[Callable] = None, /, *, use_cache: bool = True
) -> DependencyParameter:
    return DependencyParameter(dependency=dependency, use_cache=use_cache)


def Promise(
    promised_type: Union[None, Type[Request], Type[Response]] = None, /
) -> PromiseParameter:
    return PromiseParameter(promised_type=promised_type)
