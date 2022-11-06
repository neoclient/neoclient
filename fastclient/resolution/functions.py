from dataclasses import dataclass
from typing import Any, List, Optional, TypeVar

from httpx import Cookies, Headers, QueryParams, Response

from .typing import ResolutionFunction

__all__: List[str] = [
    "BodyResolutionFunction",
    "CookieResolutionFunction",
    "CookiesResolutionFunction",
    "HeaderResolutionFunction",
    "HeadersResolutionFunction",
    "QueryResolutionFunction",
    "QueriesResolutionFunction",
]

T = TypeVar("T")


@dataclass
class QueryResolutionFunction(ResolutionFunction[Optional[str]]):
    name: str

    def __call__(self, response: Response, /) -> Optional[str]:
        return response.request.url.params.get(self.name)


@dataclass
class HeaderResolutionFunction(ResolutionFunction[Optional[str]]):
    name: str

    def __call__(self, response: Response, /) -> Optional[str]:
        return response.headers.get(self.name)


@dataclass
class CookieResolutionFunction(ResolutionFunction[Optional[str]]):
    name: str

    def __call__(self, response: Response, /) -> Optional[str]:
        return response.cookies.get(self.name)


class QueriesResolutionFunction(ResolutionFunction[QueryParams]):
    @staticmethod
    def __call__(response: Response, /) -> QueryParams:
        return response.request.url.params


class HeadersResolutionFunction(ResolutionFunction[Headers]):
    @staticmethod
    def __call__(response: Response, /) -> Headers:
        return response.headers


class CookiesResolutionFunction(ResolutionFunction[Cookies]):
    @staticmethod
    def __call__(response: Response, /) -> Cookies:
        return response.cookies


class BodyResolutionFunction(ResolutionFunction[Any]):
    @staticmethod
    def __call__(response: Response, /) -> Any:
        # TODO: Massively improve this implementation
        return response.json()
