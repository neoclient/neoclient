from annotate.utils import get_annotations

from neoclient.annotations import (
    service_middleware,
    service_request_depends,
    service_response,
    service_response_depends,
)
from neoclient.enums import Entity
from neoclient.models import Request, Response
from neoclient.typing import CallNext


def test_service_middleware() -> None:
    @service_middleware
    def some_service_middleware(_, call_next: CallNext, request: Request) -> Response:
        return call_next(request)

    assert get_annotations(some_service_middleware) == {Entity.MIDDLEWARE: None}


def test_service_response() -> None:
    @service_response
    def some_service_response() -> None:
        return None

    assert get_annotations(some_service_response) == {Entity.RESPONSE: None}


def test_service_request_depends() -> None:
    @service_request_depends
    def request_dependency() -> None:
        return None

    assert get_annotations(request_dependency) == {Entity.REQUEST_DEPENDENCY: None}


def test_service_response_depends() -> None:
    @service_response_depends
    def response_dependency() -> None:
        return None

    assert get_annotations(response_dependency) == {Entity.RESPONSE_DEPENDENCY: None}
