from dataclasses import dataclass
from typing import Any, Callable, ClassVar, Dict, Generic, Literal, Optional, TypeVar, Union
from sentinel import Missing
from abc import ABC

from .enums import ParamType
from .default import Default, Sentinel

T = TypeVar("T")


@dataclass(init=False)
class Info(ABC, Generic[T]):
    _default: Default[T]

    type: ClassVar[ParamType]

    def __init__(
        self,
        *,
        default: Union[T, Literal[Sentinel.Missing]] = Sentinel.Missing,
        default_factory: Union[Callable[[], T], Literal[Sentinel.Missing]] = Sentinel.Missing,
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
        default: T = Sentinel.Missing,
    ):
        super().__init__(default=default)

        self.name = name

    @staticmethod
    def generate_name(name: str):
        return name


class Path(Param[T]):
    type: ClassVar[ParamType] = ParamType.PATH

    @staticmethod
    def generate_name(name: str):
        return name.lower().replace("_", "-")


class Query(Param[T]):
    type: ClassVar[ParamType] = ParamType.QUERY

    @staticmethod
    def generate_name(name: str):
        return name.lower().replace("_", "-")


class Header(Param[T]):
    type: ClassVar[ParamType] = ParamType.HEADER

    @staticmethod
    def generate_name(name: str):
        return name.title().replace("_", "-")


class Params(Info[T]):
    def __init__(self, *, default_factory: Union[Callable[[], T], Missing] = Missing):
        super().__init__(default_factory=default_factory)


class Queries(Params[Dict[str, Any]]):
    type: ClassVar[ParamType] = ParamType.QUERY

    def __init__(self) -> None:
        super().__init__(default_factory=dict)


class Headers(Params[Dict[str, Any]]):
    type: ClassVar[ParamType] = ParamType.HEADER

    def __init__(self) -> None:
        super().__init__(default_factory=dict)


class Cookies(Params[Dict[str, Any]]):
    type: ClassVar[ParamType] = ParamType.COOKIE

    def __init__(self) -> None:
        super().__init__(default_factory=dict)
