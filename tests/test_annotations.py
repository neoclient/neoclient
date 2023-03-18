from annotate.utils import get_annotations

from neoclient.annotations import service_middleware, service_response
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
