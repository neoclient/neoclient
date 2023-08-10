from dataclasses import dataclass, field
from typing import Optional, Protocol, Sequence

import mediate

from .enums import HTTPHeader
from .errors import ExpectedHeaderError, ExpectedStatusCodeError
from .models import Request, Response

__all__: Sequence[str] = (
    "Middleware",
    "RequestMiddleware",
    "ExpectedStatusCodeMiddleware",
    "raise_for_status",
)


class Middleware(mediate.Middleware[Request, Response]):
    pass


class RequestMiddleware(Protocol):
    def __call__(self, request: Request, /) -> Response:
        ...


@dataclass(init=False)
class ExpectedStatusCodeMiddleware:
    codes: Sequence[int] = field(default_factory=list)

    def __init__(self, *codes: int) -> None:
        self.codes = codes

    def __call__(self, call_next: RequestMiddleware, request: Request, /) -> Response:
        response: Response = call_next(request)

        if response.status_code not in self.codes:
            raise ExpectedStatusCodeError(
                f"Response contained an unexpected status code: {response.status_code}"
            )

        return response


@dataclass
class ExpectedHeaderMiddleware:
    name: str
    value: Optional[str] = None

    def __call__(self, call_next: RequestMiddleware, request: Request, /) -> Response:
        response: Response = call_next(request)

        if self.name not in response.headers:
            raise ExpectedHeaderError(name=self.name)

        header_value: str = response.headers[self.name]

        if self.value is not None and header_value != self.value:
            raise ExpectedHeaderError(
                name=self.name, value=header_value, expected_value=self.value
            )

        return response


@dataclass
class ExpectedContentTypeMiddleware:
    content_type: str

    def __call__(self, call_next: RequestMiddleware, request: Request, /) -> Response:
        # NOTE: In the future this should parse the content type to support
        # lenient checking.
        # For example, 'application/json+foo' should likely be an acceptable
        # value when expecting a lenient form of 'application/json'
        return ExpectedHeaderMiddleware(HTTPHeader.CONTENT_TYPE, self.content_type)(
            call_next, request
        )


def raise_for_status(call_next: RequestMiddleware, request: Request, /) -> Response:
    response: Response = call_next(request)

    response.raise_for_status()

    return response
