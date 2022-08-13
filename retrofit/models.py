from dataclasses import dataclass
from typing import Optional


@dataclass
class RequestSpecification:
    method: str
    endpoint: str
    params: Optional[dict] = None
