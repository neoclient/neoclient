from typing import Any, Callable, Optional, Type, TypeVar, Union

from httpx import Request, Response
from param.typing import Supplier
from pydantic.fields import UndefinedType, Undefined

from . import parameters

T = TypeVar("T")


def Header(
    alias: Optional[str] = None,
    *,
    default: Union[Any, UndefinedType] = Undefined,
    default_factory: Optional[Supplier[Any]] = None,
) -> parameters.Header:
    return parameters.Header(
        alias=alias, default=default, default_factory=default_factory
    )


def Query(
    alias: Optional[str] = None,
    *,
    default: Union[Any, UndefinedType] = Undefined,
    default_factory: Optional[Supplier[Any]] = None,
) -> parameters.Query:
    return parameters.Query(
        alias=alias, default=default, default_factory=default_factory
    )


def Path(
    alias: Optional[str] = None,
    *,
    default: Union[Any, UndefinedType] = Undefined,
    default_factory: Optional[Supplier[Any]] = None,
) -> parameters.Path:
    return parameters.Path(
        alias=alias, default=default, default_factory=default_factory
    )


def Cookie(
    alias: Optional[str] = None,
    *,
    default: Union[Any, UndefinedType] = Undefined,
    default_factory: Optional[Supplier[Any]] = None,
) -> parameters.Cookie:
    return parameters.Cookie(
        alias=alias, default=default, default_factory=default_factory
    )


def Body(
    alias: Optional[str] = None,
    *,
    default: Union[Any, UndefinedType] = Undefined,
    default_factory: Optional[Supplier[Any]] = None,
    embed: bool = False,
) -> parameters.Body:
    return parameters.Body(
        alias=alias,
        default=default,
        default_factory=default_factory,
        embed=embed,
    )


def Headers() -> parameters.Headers:
    return parameters.Headers()


def QueryParams() -> parameters.QueryParams:
    return parameters.QueryParams()


def Cookies() -> parameters.Cookies:
    return parameters.Cookies()


def PathParams() -> parameters.PathParams:
    return parameters.PathParams()


def Depends(
    dependency: Optional[Callable[..., T]] = None, /, *, use_cache: bool = True
) -> parameters.Depends[T]:
    return parameters.Depends(dependency, use_cache=use_cache)


def Promise(
    promised_type: Union[None, Type[Request], Type[Response]] = None, /
) -> parameters.Promise:
    return parameters.Promise(promised_type)
