from dataclasses import dataclass
from typing import Any, Callable, Optional, Sequence, Type, TypeVar

from httpx import URL
from mediate.protocols import MiddlewareCallable, MiddlewareMethod

from neoclient.specification import ClientSpecification

from .api import Decorator

from ..annotations import (
    service_middleware,
    service_request_dependency,
    service_response,
    service_response_dependency,
)
from ..models import Request, Response
from ..typing import Dependency

__all__ = ("service",)

C = TypeVar("C", bound=Callable[..., Any])
M = TypeVar(
    "M", MiddlewareCallable[Request, Response], MiddlewareMethod[Request, Response]
)


@dataclass
class ServiceDecoratorImpl(Decorator):
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

    def decorate_client(self, client: ClientSpecification, /) -> None:
        if self.base_url is not None:
            client.options.base_url = URL(self.base_url)
        if self.middlewares is not None:
            client.middleware.add_all(self.middlewares)
        if self.default_response is not None:
            client.default_response = self.default_response
        if self.request_dependencies is not None:
            client.request_dependencies.extend(self.request_dependencies)
        if self.response_dependencies is not None:
            client.response_dependencies.extend(self.response_dependencies)

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
