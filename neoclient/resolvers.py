from dataclasses import dataclass
from typing import Any, Optional, Sequence, TypeVar

from httpx import Cookies, Headers, QueryParams

from .models import Response
from .typing import ResponseResolver

__all__: Sequence[str] = (
    "BodyResolver",
    "CookieResolver",
    "CookiesResolver",
    "HeaderResolver",
    "HeadersResolver",
    "QueryResolver",
    "QueriesResolver",
    "StateResolver",
)

T = TypeVar("T")


@dataclass
class QueryResolver(ResponseResolver[Optional[Sequence[str]]]):
    name: str

    def __call__(self, response: Response, /) -> Optional[Sequence[str]]:
        params: QueryParams = response.request.url.params

        if self.name in params:
            return params.get_list(self.name)

        return None


@dataclass
class HeaderResolver(ResponseResolver[Optional[Sequence[str]]]):
    name: str

    def __call__(self, response: Response, /) -> Optional[Sequence[str]]:
        headers: Headers = response.headers

        if self.name in headers:
            return headers.get_list(self.name)

        return None


@dataclass
class CookieResolver(ResponseResolver[Optional[str]]):
    name: str

    def __call__(self, response: Response, /) -> Optional[str]:
        return response.cookies.get(self.name)


class QueriesResolver(ResponseResolver[QueryParams]):
    @staticmethod
    def __call__(response: Response, /) -> QueryParams:
        return response.request.url.params


class HeadersResolver(ResponseResolver[Headers]):
    @staticmethod
    def __call__(response: Response, /) -> Headers:
        return response.headers


class CookiesResolver(ResponseResolver[Cookies]):
    @staticmethod
    def __call__(response: Response, /) -> Cookies:
        return response.cookies


class BodyResolver(ResponseResolver[Any]):
    @staticmethod
    def __call__(response: Response, /) -> Any:
        return response.json()


@dataclass
class StateResolver(ResponseResolver[Any]):
    key: str

    def __call__(self, response: Response, /) -> Any:
        return response.state.get(self.key)
