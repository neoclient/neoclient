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
        return self._default.is_present()


class Body(Info):
    type: ParamType = ParamType.BODY


@dataclass(init=False)
class Param(Info[T]):
    name: Optional[str]
    required: bool = False

    def __init__(
        self,
        name: Optional[str] = None,
        *,
        default: Union[T, MissingType] = Missing,
        required: bool = False,
    ):
        super().__init__(default=default)

        self.name = name
        self.required = required

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

    @staticmethod
    def generate_name(name: str):
        return name.upper()


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
