from .params import Param
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Request:
    method: str
    url: str
    params: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)
    json: Optional[dict] = None
    cookies: dict = field(default_factory=dict)


@dataclass
class Specification(Request):
    fields: Dict[str, Param] = field(default_factory=dict)
