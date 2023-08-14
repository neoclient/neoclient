from typing import Any, Callable, Optional, Sequence

from pydantic import Required

from .dependence import DependencyParameter
from .params import (
    BodyParameter,
    CookieParameter,
    CookiesParameter,
    HeaderParameter,
    HeadersParameter,
    PathParameter,
    PathsParameter,
    QueriesParameter,
    QueryParameter,
    ReasonParameter,
    RequestParameter,
    ResponseParameter,
    StateParameter,
    StatusCodeParameter,
    URLParameter,
)
from .typing import Supplier

__all__: Sequence[str] = (
    "Query",
    "Header",
    "Cookie",
    "Path",
    "QueryParams",
    "Headers",
    "Cookies",
    "PathParams",
    "Body",
    "Depends",
    "URL",
    "Reason",
    "Request",
    "Response",
    "StatusCode",
)


def Query(
    name: Optional[str] = None,
    *,
    default: Any = Required,
    default_factory: Optional[Supplier[Any]] = None,
    const: Optional[bool] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    regex: Optional[str] = None,
) -> QueryParameter:
    return QueryParameter(
        default=default,
        default_factory=default_factory,
        alias=name,
        const=const,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        min_length=min_length,
        max_length=max_length,
        regex=regex,
    )


def Header(
    name: Optional[str] = None,
    *,
    default: Any = Required,
    default_factory: Optional[Supplier[Any]] = None,
    const: Optional[bool] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    regex: Optional[str] = None,
    convert_underscores: bool = True,
) -> HeaderParameter:
    return HeaderParameter(
        default=default,
        default_factory=default_factory,
        alias=name,
        const=const,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        min_length=min_length,
        max_length=max_length,
        regex=regex,
        convert_underscores=convert_underscores,
    )


def Cookie(
    name: Optional[str] = None,
    *,
    default: Any = Required,
    default_factory: Optional[Supplier[Any]] = None,
    const: Optional[bool] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    regex: Optional[str] = None,
) -> CookieParameter:
    return CookieParameter(
        default=default,
        default_factory=default_factory,
        alias=name,
        const=const,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        min_length=min_length,
        max_length=max_length,
        regex=regex,
    )


def Path(
    name: Optional[str] = None,
    *,
    default: Any = Required,
    default_factory: Optional[Supplier[Any]] = None,
    const: Optional[bool] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    regex: Optional[str] = None,
    delimiter: str = "/",
) -> PathParameter:
    return PathParameter(
        default=default,
        default_factory=default_factory,
        alias=name,
        const=const,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        min_length=min_length,
        max_length=max_length,
        regex=regex,
        delimiter=delimiter,
    )


def QueryParams(
    *,
    default: Any = Required,
    default_factory: Optional[Supplier[Any]] = None,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    unique_items: Optional[bool] = None,
) -> QueriesParameter:
    return QueriesParameter(
        default=default,
        default_factory=default_factory,
        min_items=min_items,
        max_items=max_items,
        unique_items=unique_items,
    )


def Headers(
    *,
    default: Any = Required,
    default_factory: Optional[Supplier[Any]] = None,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    unique_items: Optional[bool] = None,
) -> HeadersParameter:
    return HeadersParameter(
        default=default,
        default_factory=default_factory,
        min_items=min_items,
        max_items=max_items,
        unique_items=unique_items,
    )


def Cookies(
    *,
    default: Any = Required,
    default_factory: Optional[Supplier[Any]] = None,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    unique_items: Optional[bool] = None,
) -> CookiesParameter:
    return CookiesParameter(
        default=default,
        default_factory=default_factory,
        min_items=min_items,
        max_items=max_items,
        unique_items=unique_items,
    )


def PathParams(
    *,
    default: Any = Required,
    default_factory: Optional[Supplier[Any]] = None,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    unique_items: Optional[bool] = None,
    delimiter: str = "/",
) -> PathsParameter:
    return PathsParameter(
        default=default,
        default_factory=default_factory,
        min_items=min_items,
        max_items=max_items,
        unique_items=unique_items,
        delimiter=delimiter,
    )


def Body(
    *,
    default: Any = Required,
    default_factory: Optional[Supplier[Any]] = None,
    alias: Optional[str] = None,
    embed: bool = False,
) -> BodyParameter:
    return BodyParameter(
        alias=alias,
        default=default,
        default_factory=default_factory,
        embed=embed,
    )


def Depends(
    dependency: Optional[Callable] = None,
    /,
    *,
    use_cache: bool = True,
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


def Reason() -> ReasonParameter:
    return ReasonParameter()


def State(
    name: Optional[str] = None,
    *,
    default: Any = Required,
    default_factory: Optional[Supplier[Any]] = None,
) -> StateParameter:
    return StateParameter(
        default=default,
        default_factory=default_factory,
        alias=name,
    )
