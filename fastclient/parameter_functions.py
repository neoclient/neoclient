from typing import Any, Callable, List, Optional, Union

from pydantic.fields import Undefined, UndefinedType

from .dependencies import DependencyParameter
from .parameters import (
    BodyParameter,
    CookieParameter,
    CookiesParameter,
    HeaderParameter,
    HeadersParameter,
    PathParameter,
    PathsParameter,
    QueriesParameter,
    QueryParameter,
    RequestParameter,
    ResponseParameter,
    StatusCodeParameter,
    URLParameter,
)
from .typing import Supplier

__all__: List[str] = [
    "Query",
    "Header",
    "Cookie",
    "Path",
    "Queries",
    "Headers",
    "Cookies",
    "Paths",
    "Body",
    "Depends",
    "URL",
    "Request",
    "Response",
    "StatusCode",
]


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


def URL() -> URLParameter:
    return URLParameter()


def Request() -> RequestParameter:
    return RequestParameter()


def Response() -> ResponseParameter:
    return ResponseParameter()


def StatusCode() -> StatusCodeParameter:
    return StatusCodeParameter()
