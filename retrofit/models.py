from .params import Info
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Request:
    method: str
    url: str
    params: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)
    json: dict = field(default_factory=dict)
    cookies: dict = field(default_factory=dict)


@dataclass
class Specification(Request):
    fields: Dict[str, Info] = field(default_factory=dict)
