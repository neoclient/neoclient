from dataclasses import dataclass, field
from typing import Optional, Protocol, Sequence

import mediate
from httpx import Request, Response

from .errors import ExpectedStatusCodeError, ExpectedHeaderError

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
            raise ExpectedHeaderError(f"Response missing required header {self.name!r}")
        elif self.value is not None and response.headers[self.name] != self.value:
            raise ExpectedHeaderError(
                f"Response header {self.name!r} has incorrect value. Expected {self.value!r}, got {response.headers[self.name]!r}"
            )

        return response


def raise_for_status(call_next: RequestMiddleware, request: Request, /) -> Response:
    response: Response = call_next(request)

    response.raise_for_status()

    return response
