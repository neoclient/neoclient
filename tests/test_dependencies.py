from http import HTTPStatus
from fastclient.enums import HttpMethod
from fastclient.dependencies import DependencyResolutionFunction
from httpx import Request, Response


def test_DependencyResolutionFunction() -> None:
    def dependency(response: Response, /) -> Response:
        return response

    response: Response = Response(
        HTTPStatus.OK, request=Request(HttpMethod.GET, "https://foo.com/")
    )

    assert DependencyResolutionFunction(dependency)(response) == response
