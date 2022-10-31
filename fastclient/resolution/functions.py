from dataclasses import dataclass
from typing import Any, Callable, List, Mapping, Optional, Type, TypeVar

from httpx import Response, Headers, Cookies, QueryParams
from pydantic import BaseModel

from .typing import ResolutionFunction

__all__: List[str] = [
    "CookieResolutionFunction",
    "CookiesResolutionFunction",
    "DependencyResolutionFunction",
    "HeaderResolutionFunction",
    "HeadersResolutionFunction",
    "QueryResolutionFunction",
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
        return response.headers.get(self.name)


@dataclass
class QueriesResolutionFunction(ResolutionFunction[QueryParams]):
    def __call__(self, response: Response, /) -> QueryParams:
        return response.request.url.params


@dataclass
class HeadersResolutionFunction(ResolutionFunction[Headers]):
    def __call__(self, response: Response, /) -> Headers:
        return response.headers


@dataclass
class CookiesResolutionFunction(ResolutionFunction[Cookies]):
    def __call__(self, response: Response, /) -> Cookies:
        return response.cookies


@dataclass
class DependencyResolutionFunction(ResolutionFunction[T]):
    model_cls: Type[BaseModel]
    dependency: Callable[..., T]
    parameters: Mapping[str, ResolutionFunction]

    def __call__(self, response: Response, /) -> T:
        arguments: Mapping[str, Any] = {
            parameter: resolution_function(response)
            for parameter, resolution_function in self.parameters.items()
        }

        model: BaseModel = self.model_cls(**arguments)

        validated_arguments: Mapping[str, Any] = model.dict()

        return self.dependency(**validated_arguments)
