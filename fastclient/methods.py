from typing import Any, Callable, Optional, TypeVar

from typing_extensions import ParamSpec

from .enums import HttpMethod
from .client import FastClient

PS = ParamSpec("PS")
RT = TypeVar("RT")

DEFAULT_CLIENT: FastClient = FastClient(client=None)


def request(
    method: str, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    return DEFAULT_CLIENT.request(method, endpoint, response=response)


def put(
    endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    return request(HttpMethod.PUT, endpoint, response=response)


def get(
    endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    return request(HttpMethod.GET, endpoint, response=response)


def post(
    endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    return request(HttpMethod.POST, endpoint, response=response)


def head(
    endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    return request(HttpMethod.HEAD, endpoint, response=response)


def patch(
    endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    return request(HttpMethod.PATCH, endpoint, response=response)


def delete(
    endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    return request(HttpMethod.DELETE, endpoint, response=response)


def options(
    endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    return request(HttpMethod.OPTIONS, endpoint, response=response)
