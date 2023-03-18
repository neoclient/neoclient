import inspect
from typing import Any, Callable, Dict, Optional, Sequence, Tuple, Type

from mediate.protocols import MiddlewareCallable

from .annotations.api import has_annotation
from .annotations.enums import Annotation
from .client import Client
from .errors import ServiceInitialisationError
from .middleware import Middleware
from .models import Request, Response
from .operation import Operation, get_operation, has_operation
from .specification import ClientSpecification

__all__: Sequence[str] = ("Service",)


class ServiceMeta(type):
    _spec: ClientSpecification

    def __new__(
        mcs: Type["ServiceMeta"], name: str, bases: Tuple[type], attrs: Dict[str, Any]
    ) -> type:
        def __init__(self) -> None:
            service_middleware: Sequence[MiddlewareCallable[Request, Response]] = [
                member
                for _, member in inspect.getmembers(self)
                if has_annotation(member, Annotation.MIDDLEWARE)
            ]
            service_responses: Sequence[Callable] = [
                member
                for _, member in inspect.getmembers(self)
                if has_annotation(member, Annotation.RESPONSE)
            ]

            if len(service_responses) > 1:
                raise ServiceInitialisationError(
                    f"Found {len(service_responses)} service responses, expected at most 1"
                )

            middleware: Middleware = Middleware()

            middleware.add_all(self._spec.middleware.record)
            middleware.add_all(service_middleware)

            response: Optional[Callable[..., Any]] = self._spec.default_response

            # If a service-level response was defined, use this instead of the one
            # defined within the specification
            if service_responses:
                response = service_responses[0]

            self._client = Client(
                client=self._spec.options.build(),
                middleware=middleware,
                default_response=response,
            )

            for member_name, member in inspect.getmembers(self):
                if not has_operation(member):
                    continue

                bound_operation_func: Callable = self._client.bind(member)
                bound_operation_method: Callable = bound_operation_func.__get__(self)

                bound_operation: Operation = get_operation(bound_operation_method)

                bound_operation.func = bound_operation_method

                setattr(self, member_name, bound_operation_method)

        attrs["_spec"] = ClientSpecification()
        attrs["__init__"] = __init__

        typ: type = super().__new__(mcs, name, bases, attrs)

        return typ


class Service(metaclass=ServiceMeta):
    _client: Client

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"
