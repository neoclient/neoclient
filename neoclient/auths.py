from abc import ABC, abstractmethod
from base64 import b64encode
from dataclasses import dataclass
from typing import Sequence, TypeVar

import httpx

from .enums import HTTPHeader

__all__: Sequence[str] = (
    "Auth",
    "BasicAuth",
)

R = TypeVar("R", bound=httpx.Request)


class Auth(ABC):
    @abstractmethod
    def auth(self, request: R, /) -> R:
        raise NotImplementedError


@dataclass
class BasicAuth(Auth):
    username: str
    password: str

    def auth(self, request: R, /) -> R:
        request.headers[HTTPHeader.AUTHORIZATION] = self.authorization

        return request

    @property
    def authorization(self) -> str:
        token: str = b64encode(f"{self.username}:{self.password}".encode()).decode()

        return f"Basic {token}"
