from dataclasses import dataclass
from typing import Any, Callable, List, Mapping, Optional, Type, TypeVar

from httpx import Response, Headers, Cookies, QueryParams
from pydantic import BaseModel

from .typing import ResolutionFunction
from ..typing import Resolver
from ..parameters import BaseParameter

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


@dataclass
class DependencyResolutionFunction(ResolutionFunction[T]):
    model_cls: Type[BaseModel]
    dependency: Callable[..., T]
    parameters: Mapping[str, BaseParameter]

    def __call__(self, response: Response, /) -> T:
        arguments: Mapping[str, Any] = {
            parameter_name: parameter.resolve(response)
            for parameter_name, parameter in self.parameters.items()
        }

        model: BaseModel = self.model_cls(**arguments)

        validated_arguments: Mapping[str, Any] = model.dict()

        return self.dependency(**validated_arguments)
