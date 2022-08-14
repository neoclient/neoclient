from dataclasses import dataclass, field
from typing import Any
from sentinel import Missing

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
class FieldInfo:
    name: str
    default: Any = Missing
    # default_factory

@dataclass
class Path(FieldInfo):
    pass

@dataclass
class Param(FieldInfo):
    pass

@dataclass
class Header(FieldInfo):
    pass