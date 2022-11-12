from dataclasses import dataclass
from typing import Any, Optional, Sequence, TypeVar

from httpx import Cookies, Headers, QueryParams, Response

from ..typing import Resolver

__all__: Sequence[str] = (
    "BodyResolver",
    "CookieResolver",
    "CookiesResolver",
    "HeaderResolver",
    "HeadersResolver",
    "QueryResolver",
    "QueriesResolver",
)

T = TypeVar("T")


@dataclass
class QueryResolver(Resolver[Optional[str]]):
    name: str

    def __call__(self, response: Response, /) -> Optional[str]:
        return response.request.url.params.get(self.name)


@dataclass
class HeaderResolver(Resolver[Optional[str]]):
    name: str

    def __call__(self, response: Response, /) -> Optional[str]:
        return response.headers.get(self.name)


@dataclass
class CookieResolver(Resolver[Optional[str]]):
    name: str

    def __call__(self, response: Response, /) -> Optional[str]:
        return response.cookies.get(self.name)


class QueriesResolver(Resolver[QueryParams]):
    @staticmethod
    def __call__(response: Response, /) -> QueryParams:
        return response.request.url.params


class HeadersResolver(Resolver[Headers]):
    @staticmethod
    def __call__(response: Response, /) -> Headers:
        return response.headers


class CookiesResolver(Resolver[Cookies]):
    @staticmethod
    def __call__(response: Response, /) -> Cookies:
        return response.cookies


class BodyResolver(Resolver[Any]):
    @staticmethod
    def __call__(response: Response, /) -> Any:
        # TODO: Massively improve this implementation
        return response.json()
