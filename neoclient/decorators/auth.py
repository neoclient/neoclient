from typing import Any, Callable, Sequence, Type, TypeVar

from ..auths import Auth, BasicAuth
from ..middlewares import AuthMiddleware
from ..services import Service
from .middleware import middleware

__all__: Sequence[str] = (
    "auth",
    "basic_auth",
)

CS = TypeVar("CS", Callable[..., Any], Type[Service])


def auth(auth: Auth, /) -> Callable[[CS], CS]:
    return middleware(AuthMiddleware(auth))


def basic_auth(username: str, password: str) -> Callable[[CS], CS]:
    return auth(BasicAuth(username, password))
