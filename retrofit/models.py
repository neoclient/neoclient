from dataclasses import dataclass


@dataclass
class RequestSpecification:
    method: str
    endpoint: str
