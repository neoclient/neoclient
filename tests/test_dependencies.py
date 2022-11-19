from http import HTTPStatus

from httpx import Request, Response

from fastclient.dependencies import DependencyResolver
from fastclient.enums import HttpMethod


def test_DependencyResolver() -> None:
    def dependency(response: Response, /) -> Response:
        return response

    response: Response = Response(
        HTTPStatus.OK, request=Request(HttpMethod.GET, "https://foo.com/")
    )

    assert DependencyResolver(dependency)(response) == response
