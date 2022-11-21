from dataclasses import dataclass, field
from typing import Protocol, Sequence

import mediate
from httpx import Request, Response

from .errors import UnexpectedStatusCodeError

__all__: Sequence[str] = (
    "Middleware",
    "RequestMiddleware",
    "StatusCodeMiddleware",
    "raise_for_status",
)


class Middleware(mediate.Middleware[Request, Response]):
    pass


class RequestMiddleware(Protocol):
    def __call__(self, request: Request, /) -> Response:
        ...


@dataclass(init=False)
class StatusCodeMiddleware:
    codes: Sequence[int] = field(default_factory=list)

    def __init__(self, *codes: int) -> None:
        self.codes = codes

    def __call__(self, call_next: RequestMiddleware, request: Request, /) -> Response:
        response: Response = call_next(request)

        if response.status_code not in self.codes:
            raise UnexpectedStatusCodeError(
                f"Response contained an unexpected status code: {response.status_code}"
            )

        return response


def raise_for_status(call_next: RequestMiddleware, request: Request, /) -> Response:
    response: Response = call_next(request)

    response.raise_for_status()

    return response
