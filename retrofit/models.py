from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RequestSpecification:
    method: str
    endpoint: str
    params: dict = field(default_factory=dict)
    path_params: dict = field(default_factory=dict)

@dataclass
class Request:
    method: str
    url: str
    params: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)
    body: str = ""


@dataclass
class Path:
    field: str

@dataclass
class Param:
    field: str