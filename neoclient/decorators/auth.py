from typing import Sequence

from .api import CommonDecorator
from ..auths import Auth, BasicAuth
from ..middlewares import AuthMiddleware
from .middleware import middleware

__all__: Sequence[str] = (
    "auth",
    "basic_auth",
)


def auth(auth: Auth, /) -> CommonDecorator:
    return middleware(AuthMiddleware(auth))


def basic_auth(username: str, password: str) -> CommonDecorator:
    return auth(BasicAuth(username, password))
