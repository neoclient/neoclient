from typing import Any, Callable, Optional, Type, Union

from httpx import Request, Response
from param.typing import Supplier
from pydantic.fields import Undefined, UndefinedType

from . import parameters


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


def Headers(
    *,
    default: Union[Any, UndefinedType] = Undefined,
    default_factory: Optional[Supplier[Any]] = None,
) -> parameters.Headers:
    return parameters.Headers(
        default=default,
        default_factory=default_factory,
    )


def QueryParams(
    *,
    default: Union[Any, UndefinedType] = Undefined,
    default_factory: Optional[Supplier[Any]] = None,
) -> parameters.QueryParams:
    return parameters.QueryParams(
        default=default,
        default_factory=default_factory,
    )


def Cookies(
    *,
    default: Union[Any, UndefinedType] = Undefined,
    default_factory: Optional[Supplier[Any]] = None,
) -> parameters.Cookies:
    return parameters.Cookies(
        default=default,
        default_factory=default_factory,
    )


def PathParams(
    *,
    default: Union[Any, UndefinedType] = Undefined,
    default_factory: Optional[Supplier[Any]] = None,
) -> parameters.PathParams:
    return parameters.PathParams(
        default=default,
        default_factory=default_factory,
    )


def Depends(
    dependency: Optional[Callable] = None, /, *, use_cache: bool = True
) -> parameters.Depends:
    return parameters.Depends(dependency=dependency, use_cache=use_cache)


def Promise(
    promised_type: Union[None, Type[Request], Type[Response]] = None, /
) -> parameters.Promise:
    return parameters.Promise(promised_type=promised_type)
