from dataclasses import dataclass
from typing import Any, Callable, Mapping, Optional, Type, TypeVar

from httpx import Response
from pydantic import BaseModel

from .typing import ResolutionFunction

T = TypeVar("T")


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
