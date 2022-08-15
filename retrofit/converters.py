from typing import Protocol, TypeVar
from .models import Request
from httpx import Response
import httpx

T_co = TypeVar("T_co", covariant=True)
R_cont = TypeVar("R_cont", contravariant=True)
C_co = TypeVar("C_co", covariant=True)


class Resolver(Protocol[T_co]):
    def resolve(self, request: Request, /) -> T_co:
        ...


class Converter(Protocol[R_cont, C_co]):
    def convert(self, resolved: R_cont, /) -> C_co:
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
