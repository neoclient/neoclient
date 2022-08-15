from typing import Generic, Protocol, TypeVar
from .models import Request
from httpx import Response
import httpx

T = TypeVar("T")
RT = TypeVar("RT")
CT = TypeVar("CT")


class Resolver(Protocol, Generic[T]):
    def resolve(self, request: Request, /) -> T:
        ...


class Converter(Protocol[RT, CT]):
    def convert(self, resolved: RT, /) -> CT:
        ...


class IdentityResolver(Resolver[Request]):
    def resolve(self, request: Request, /) -> Request:
        return request


class IdentityConverter(Converter[Request, Request]):
    def convert(self, resolved: Request, /) -> Request:
        return resolved


class HttpxResolver(Resolver[Response]):
    def resolve(self, request: Request, /) -> Response:
        return httpx.request(
            method=request.method,
            url=request.url,
            params=request.params,
            headers=request.headers,
            # body
        )


class HttpxJsonConverter(Converter[Response, dict]):
    def convert(self, resolved: Response, /) -> dict:
        return resolved.json()