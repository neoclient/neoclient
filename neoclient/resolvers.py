from dataclasses import dataclass
from typing import Any, Optional, Sequence, TypeVar

from httpx import Cookies, Headers, QueryParams

from .models import PreRequest, Response, State
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
class QueryResolver:
    name: str

    def resolve_request(self, request: PreRequest, /) -> Optional[Sequence[str]]:
        return self.resolve(request.params)

    def resolve_response(self, response: Response, /) -> Optional[Sequence[str]]:
        return self.resolve(response.request.url.params)

    def resolve(self, query_params: QueryParams, /) -> Optional[Sequence[str]]:
        if self.name in query_params:
            return query_params.get_list(self.name)

        return None


@dataclass
class HeaderResolver:
    name: str

    def resolve_request(self, request: PreRequest, /) -> Optional[Sequence[str]]:
        return self.resolve(request.headers)

    def resolve_response(self, response: Response, /) -> Optional[Sequence[str]]:
        return self.resolve(response.headers)
    
    def resolve(self, headers: Headers, /) -> Optional[Sequence[str]]:
        if self.name in headers:
            return headers.get_list(self.name)

        return None


@dataclass
class CookieResolver:
    name: str

    def resolve_request(self, request: PreRequest, /) -> Optional[str]:
        return self.resolve(request.cookies)

    def resolve_response(self, response: Response, /) -> Optional[str]:
        return self.resolve(response.cookies)
    
    def resolve(self, cookies: Cookies, /) -> Optional[str]:
        return cookies.get(self.name)


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
class StateResolver:
    key: str

    def resolve_request(self, request: PreRequest, /) -> Any:
        return self.resolve(request.state)

    def resolve_response(self, response: Response, /) -> Any:
        return self.resolve(response.state)
    
    def resolve(self, state: State, /) -> Any:
        return state.get(self.key)