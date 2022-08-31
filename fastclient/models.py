from .params import Param
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Sequence, Tuple, Union
import httpx


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


@dataclass
class ClientConfig:
    base_url: Union[httpx.URL, str] = ""
    headers: Union[
        httpx.Headers,
        Dict[str, str],
        Dict[bytes, bytes],
        Sequence[Tuple[str, str]],
        Sequence[Tuple[bytes, bytes]],
        None,
    ] = None

    def build(self) -> httpx.Client:
        return httpx.Client(
            base_url=self.base_url,
            headers=self.headers,
        )

    def is_default(self) -> bool:
        return all(
            (
                self.base_url == "",
                self.headers == None,
            )
        )

    @classmethod
    def from_client(cls, client: httpx.Client, /) -> "ClientConfig":
        return cls(
            base_url=client.base_url,
            headers=client.headers,
        )
