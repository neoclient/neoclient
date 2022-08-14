from dataclasses import dataclass, field, InitVar
from typing import Callable, ClassVar, Generic, TypeVar, Union
from sentinel import Missing
from abc import ABC

from .enums import FieldType

T = TypeVar("T")


@dataclass
class RequestSpecification:
    method: str
    endpoint: str
    params: dict = field(default_factory=dict)
    path_params: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)


@dataclass
class Request:
    method: str
    url: str
    params: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)
    body: str = ""


@dataclass(init=False)
class Info(ABC, Generic[T]):
    _has_default: InitVar[bool]
    _default_factory: InitVar[Callable[[], T]]
    type: ClassVar[FieldType]

    def __init__(
        self,
        *,
        default: Union[T, Missing] = Missing,
        default_factory: Union[Callable[[], T], Missing] = Missing
    ):
        if default is not Missing and default_factory is not Missing:
            raise ValueError("cannot specify both default and default_factory")

        self._has_default = True

        if default is Missing and default_factory is Missing:
            self._has_default = False
            self._default_factory = lambda: Missing
        elif default is not Missing:
            self._default_factory = lambda: default
        else:
            self._default_factory = default_factory

    @property
    def default(self) -> T:
        return self._default_factory()

    def has_default(self) -> bool:
        return self._has_default

@dataclass(init=False)
class FieldInfo(Info[T]):
    name: str

    def __init__(
        self,
        name: str,
        *,
        default: Union[T, Missing] = Missing,
        default_factory: Union[Callable[[], T], Missing] = Missing
    ):
        super().__init__(default=default, default_factory=default_factory)

        self.name = name


class Path(FieldInfo[T]):
    type: ClassVar[FieldType] = FieldType.PATH


class Query(FieldInfo[T]):
    type: ClassVar[FieldType] = FieldType.QUERY


class Header(FieldInfo[T]):
    type: ClassVar[FieldType] = FieldType.HEADER

class QueryDict(Info[T]):
    type: ClassVar[FieldType] = FieldType.QUERY_DICT

class HeaderDict(Info[T]):
    type: ClassVar[FieldType] = FieldType.HEADER_DICT