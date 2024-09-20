from abc import ABC, abstractmethod
from base64 import b64encode
from dataclasses import dataclass
from typing import TypeVar

import httpx

from .enums import HTTPHeader

__all__ = (
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
    def credentials(self) -> str:
        return f"{self.username}:{self.password}"

    @property
    def token(self) -> str:
        return b64encode(self.credentials.encode()).decode()

    @property
    def authorization(self) -> str:
        return f"Basic {self.token}"
