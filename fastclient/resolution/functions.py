from dataclasses import dataclass
from typing import Any, Callable, List, Mapping, Optional, Tuple, Type, TypeVar

from httpx import Cookies, Headers, QueryParams, Response
from pydantic import BaseModel

from .. import utils
from ..parameters import BaseParameter
from .typing import ResolutionFunction

__all__: List[str] = [
    "BodyResolutionFunction",
    "CookieResolutionFunction",
    "CookiesResolutionFunction",
    "DependencyResolutionFunction",
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

        args: Tuple[Any, ...]
        kwargs: Mapping[str, Any]
        args, kwargs = utils.unpack_arguments(self.dependency, validated_arguments)

        return self.dependency(*args, **kwargs)
