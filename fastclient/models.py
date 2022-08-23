from .params import Param
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional


@dataclass
class Request:
    method: str
    url: str
    params: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)
    json: Optional[dict] = None
    cookies: dict = field(default_factory=dict)


@dataclass
class Specification:
    request: Request
    response: Optional[Callable[..., Any]] = None
    params: Dict[str, Param] = field(default_factory=dict)
