from neoclient.auth import BasicAuth
from neoclient.enums import HTTPHeader
from neoclient.models import Request

from .utils import build_request


def test_BasicAuth() -> None:
    username: str = "username"
    password: str = "password"
    token: str = "dXNlcm5hbWU6cGFzc3dvcmQ="
    credentials: str = f"{username}:{password}"
    authorization = f"Basic {token}"

    basic_auth: BasicAuth = BasicAuth(username, password)

    assert basic_auth.credentials == credentials
    assert basic_auth.token == token
    assert basic_auth.authorization == authorization

    request: Request = build_request()

    assert request.headers.get(HTTPHeader.AUTHORIZATION) is None

    authed_request: Request = basic_auth.auth(request)

    assert authed_request.headers.get(HTTPHeader.AUTHORIZATION) == authorization
