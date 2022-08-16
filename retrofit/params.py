from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, Optional, TypeVar, Union
from abc import ABC

from .enums import ParamType
from .default import Default
from .sentinels import Missing, MissingType

T = TypeVar("T")


class Info(ABC, Generic[T]):
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
        return self._default.present()


@dataclass(init=False)
class Param(Info[T]):
    name: Optional[str]

    def __init__(
        self,
        name: Optional[str] = None,
        *,
        default: Union[T, MissingType] = Missing,
    ):
        super().__init__(default=default)

        self.name = name

    @staticmethod
    def generate_name(name: str):
        return name


class Path(Param[T]):
    type: ParamType = ParamType.PATH

    @staticmethod
    def generate_name(name: str):
        return name.lower().replace("_", "-")


class Query(Param[T]):
    type: ParamType = ParamType.QUERY

    @staticmethod
    def generate_name(name: str):
        return name.lower().replace("_", "-")


class Header(Param[T]):
    type: ParamType = ParamType.HEADER

    @staticmethod
    def generate_name(name: str):
        return name.title().replace("_", "-")


class Cookie(Param[T]):
    type: ParamType = ParamType.COOKIE


class Params(Info[T]):
    def __init__(
        self, *, default_factory: Union[Callable[[], T], MissingType] = Missing
    ):
        super().__init__(default_factory=default_factory)


class Queries(Params[Dict[str, Any]]):
    type: ParamType = ParamType.QUERY


class Headers(Params[Dict[str, Any]]):
    type: ParamType = ParamType.HEADER


class Cookies(Params[Dict[str, Any]]):
    type: ParamType = ParamType.COOKIE
