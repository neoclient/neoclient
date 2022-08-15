from dataclasses import dataclass, field, InitVar
from typing import Callable, ClassVar, Dict, Generic, Optional, TypeVar, Union
from sentinel import Missing
from abc import ABC

from .enums import FieldType

T = TypeVar("T")


@dataclass(init=False)
class Info(ABC, Generic[T]):
    _default: InitVar[Union[T, Missing]]
    _default_factory: InitVar[Union[Callable[[], T], Missing]]

    type: ClassVar[FieldType]

    def __init__(
        self,
        *,
        default: Union[T, Missing] = Missing,
        default_factory: Union[Callable[[], T], Missing] = Missing
    ):
        if default is not Missing and default_factory is not Missing:
            raise ValueError("cannot specify both default and default_factory")

        self._default = default
        self._default_factory = default_factory

    @property
    def default(self) -> T:
        if self._default_factory is not Missing:
            return self._default_factory()

        return self._default

    def has_default(self) -> bool:
        return self._default is not Missing or self._default_factory is not Missing


@dataclass(init=False)
class FieldInfo(Info[T]):
    name: Optional[str]

    def __init__(
        self,
        name: Optional[str] = None,
        *,
        default: Union[T, Missing] = Missing,
        default_factory: Union[Callable[[], T], Missing] = Missing
    ):
        super().__init__(default=default, default_factory=default_factory)

        self.name = name

    @staticmethod
    def generate_name(name: str):
        return name


class FieldDictInfo(Info[T]):
    pass


class Path(FieldInfo[T]):
    type: ClassVar[FieldType] = FieldType.PATH


class Query(FieldInfo[T]):
    type: ClassVar[FieldType] = FieldType.QUERY


class Header(FieldInfo[T]):
    type: ClassVar[FieldType] = FieldType.HEADER

    @staticmethod
    def generate_name(name: str):
        return name.title().replace("_", "-")

class Body(FieldInfo[T]):
    type: ClassVar[FieldType] = FieldType.BODY


class QueryDict(FieldDictInfo[T]):
    type: ClassVar[FieldType] = FieldType.QUERY


class HeaderDict(FieldDictInfo[T]):
    type: ClassVar[FieldType] = FieldType.HEADER


@dataclass
class Specification:
    method: str
    endpoint: str
    fields: Dict[str, Info] = field(default_factory=dict)


@dataclass
class Request:
    method: str
    url: str
    params: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)
    body: dict = field(default_factory=dict)
