from dataclasses import dataclass, field
from typing import Callable, Mapping, Protocol, Sequence

import mediate
from httpx import Request, Response

__all__: Sequence[str] = (
    "Middleware",
    "RequestMiddleware",
    "raise_for_status",
)


class Middleware(mediate.Middleware[Request, Response]):
    pass


class RequestMiddleware(Protocol):
    def __call__(self, request: Request, /) -> Response:
        ...


# TODO: Finish implementation...
@dataclass
class ExceptionMiddleware:
    handlers: Mapping[int, Callable[[Response], None]] = field(default_factory=dict)

    def __call__(self, call_next: RequestMiddleware, request: Request, /) -> Response:
        response: Response = call_next(request)

        if response.is_error:
            ...


def raise_for_status(call_next: RequestMiddleware, request: Request, /) -> Response:
    response: Response = call_next(request)

    response.raise_for_status()

    return response
