from dataclasses import dataclass
from typing import Callable, Optional, Sequence, Type, TypeVar

from httpx import URL
from mediate.protocols import MiddlewareCallable, MiddlewareMethod

from ..annotations import (
    service_middleware,
    service_request_depends,
    service_response,
    service_response_depends,
)
from ..models import Request, Response
from ..service import Service
from ..typing import Decorator, Dependency

__all__: Sequence[str] = ("service",)

C = TypeVar("C", bound=Callable)
M = TypeVar(
    "M", MiddlewareCallable[Request, Response], MiddlewareMethod[Request, Response]
)
S = TypeVar("S", bound=Type[Service])


@dataclass
class ServiceDecorator(Decorator[S]):
    base_url: Optional[str] = None
    middlewares: Optional[Sequence[MiddlewareCallable[Request, Response]]] = None
    default_response: Optional[Dependency] = None
    dependencies: Optional[Sequence[Dependency]] = None

    def __init__(
        self,
        base_url: Optional[str] = None,
        *,
        middleware: Optional[Sequence[MiddlewareCallable[Request, Response]]] = None,
        default_response: Optional[Dependency] = None,
        dependencies: Optional[Sequence[Dependency]] = None,
    ) -> None:
        self.base_url = base_url
        self.middlewares = middleware
        self.default_response = default_response
        self.dependencies = dependencies

    def __call__(self, target: S, /) -> S:
        if self.base_url is not None:
            target._spec.options.base_url = URL(self.base_url)
        if self.middlewares is not None:
            target._spec.middleware.add_all(self.middlewares)
        if self.default_response is not None:
            target._spec.default_response = self.default_response
        if self.dependencies is not None:
            target._spec.request_dependencies.extend(self.dependencies)

        return target

    @staticmethod
    def middleware(middleware: M, /) -> M:
        return service_middleware(middleware)

    @staticmethod
    def response(response: C, /) -> C:
        return service_response(response)

    @staticmethod
    def request_depends(dependency: C, /) -> C:
        return service_request_depends(dependency)

    @staticmethod
    def response_depends(dependency: C, /) -> C:
        return service_response_depends(dependency)


service: Type[ServiceDecorator] = ServiceDecorator
