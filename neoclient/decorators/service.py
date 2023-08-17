from dataclasses import dataclass
from typing import Optional, Sequence, Type, TypeVar

from httpx import URL
from mediate.protocols import MiddlewareCallable, MiddlewareMethod

from ..annotations import (
    service_middleware,
    service_request_dependency,
    service_response,
    service_response_dependency,
)
from ..models import Request, Response
from ..typing import Dependency
from .api import C, S, ServiceDecorator

__all__: Sequence[str] = ("service",)

M = TypeVar(
    "M", MiddlewareCallable[Request, Response], MiddlewareMethod[Request, Response]
)


@dataclass
class ServiceDecoratorImpl(ServiceDecorator):
    base_url: Optional[str] = None
    middlewares: Optional[Sequence[MiddlewareCallable[Request, Response]]] = None
    default_response: Optional[Dependency] = None
    request_dependencies: Optional[Sequence[Dependency]] = None
    response_dependencies: Optional[Sequence[Dependency]] = None

    def __init__(
        self,
        base_url: Optional[str] = None,
        *,
        middleware: Optional[Sequence[MiddlewareCallable[Request, Response]]] = None,
        default_response: Optional[Dependency] = None,
        request_dependencies: Optional[Sequence[Dependency]] = None,
        response_dependencies: Optional[Sequence[Dependency]] = None,
    ) -> None:
        self.base_url = base_url
        self.middlewares = middleware
        self.default_response = default_response
        self.request_dependencies = request_dependencies
        self.response_dependencies = response_dependencies

    def __call__(self, target: S, /) -> S:
        if self.base_url is not None:
            target._spec.options.base_url = URL(self.base_url)
        if self.middlewares is not None:
            target._spec.middleware.add_all(self.middlewares)
        if self.default_response is not None:
            target._spec.default_response = self.default_response
        if self.request_dependencies is not None:
            target._spec.request_dependencies.extend(self.request_dependencies)
        if self.response_dependencies is not None:
            target._spec.response_dependencies.extend(self.response_dependencies)

        return target

    @staticmethod
    def middleware(middleware: M, /) -> M:
        return service_middleware(middleware)

    @staticmethod
    def response(response: C, /) -> C:
        return service_response(response)

    @staticmethod
    def request_depends(dependency: C, /) -> C:
        return service_request_dependency(dependency)

    @staticmethod
    def response_depends(dependency: C, /) -> C:
        return service_response_dependency(dependency)


service: Type[ServiceDecoratorImpl] = ServiceDecoratorImpl
