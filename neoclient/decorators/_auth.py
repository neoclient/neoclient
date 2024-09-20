from ..auth import Auth, BasicAuth
from ..middleware import AuthMiddleware
from ._middleware import middleware

__all__ = ("auth", "basic_auth")

# TODO: Type responses


def auth(auth: Auth, /):
    return middleware(AuthMiddleware(auth))


def basic_auth(username: str, password: str):
    return auth(BasicAuth(username, password))
