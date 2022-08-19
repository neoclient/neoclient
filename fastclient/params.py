from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, Optional, TypeVar, Union

from .enums import ParamType
from .default import Default
from .sentinels import Missing, MissingType

T = TypeVar("T")


class Info(Generic[T]):
    _default: Default[T]

    type: ParamType

    def __init__(
        self,
        *,
        default: Union[T, MissingType] = Missing,
        default_factory: Union[Callable[[], T], MissingType] = Missing,
    ):
        self._default = Default(value=default, factory=default_factory)

    @property
    def default(self) -> T:
        return self._default.get()

    def has_default(self) -> bool:
        return self._default.is_present()


@dataclass(init=False)
class Param(Info[T]):
    alias: Optional[str]
    required: bool = False

    def __init__(
        self,
        alias: Optional[str] = None,
        *,
        default: Union[T, MissingType] = Missing,
        default_factory: Union[Callable[[], T], MissingType] = Missing,
        required: bool = False,
    ):
        super().__init__(default=default, default_factory=default_factory)

        self.alias = alias
        self.required = required

    @staticmethod
    def generate_alias(alias: str):
        return alias


class Path(Param[T]):
    type: ParamType = ParamType.PATH

    @staticmethod
    def generate_alias(alias: str):
        return alias.lower().replace("_", "-")


class Query(Param[T]):
    type: ParamType = ParamType.QUERY

    @staticmethod
    def generate_alias(alias: str):
        return alias.lower().replace("_", "-")


class Header(Param[T]):
    type: ParamType = ParamType.HEADER

    @staticmethod
    def generate_alias(alias: str):
        return alias.title().replace("_", "-")


class Cookie(Param[T]):
    type: ParamType = ParamType.COOKIE

    @staticmethod
    def generate_alias(alias: str):
        return alias.upper()


class Body(Param[T]):
    type: ParamType = ParamType.BODY

    # TODO: Override `generate_alias` to return camel case? Or expect them to use an alias.


class Params(Info[Dict[str, Any]]):
    def __init__(
        self,
        *,
        default_factory: Union[Callable[[], Dict[str, Any]], MissingType] = Missing,
    ):
        super().__init__(
            default_factory=default_factory
            if default_factory is not Missing
            else lambda: dict()
        )


class Queries(Params):
    type: ParamType = ParamType.QUERY


class Headers(Params):
    type: ParamType = ParamType.HEADER


class Cookies(Params):
    type: ParamType = ParamType.COOKIE
