from dataclasses import dataclass, field
from typing import Any, ClassVar
from sentinel import Missing
from abc import ABC

from .enums import FieldType


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


@dataclass
class FieldInfo(ABC):
    type: ClassVar[FieldType]

    name: str
    default: Any = Missing
    # TODO: default_factory


@dataclass
class Path(FieldInfo):
    type: ClassVar[FieldType] = FieldType.PATH


@dataclass
class Query(FieldInfo):
    type: ClassVar[FieldType] = FieldType.QUERY


@dataclass
class Header(FieldInfo):
    type: ClassVar[FieldType] = FieldType.HEADER
