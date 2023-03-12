import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Tuple, Type

from .annotations.api import has_annotation
from .annotations.enums import Annotation
from .client import Client
from .middleware import Middleware
from .models import ClientOptions
from .operation import Operation, get_operation, has_operation


@dataclass
class ClientSpecification:
    options: ClientOptions = field(default_factory=ClientOptions)
    middleware: Middleware = field(default_factory=Middleware)
    default_response: Optional[Callable[..., Any]] = None


class ServiceMeta(type):
    _spec: ClientSpecification

    def __new__(
        mcs: Type["ServiceMeta"], name: str, bases: Tuple[type], attrs: Dict[str, Any]
    ) -> type:
        def __init__(self) -> None:
            self._client = Client(
                client=self._spec.options.build(),
                middleware=self._spec.middleware,
                default_response=self._spec.default_response,
            )

            member_name: str
            member: Any
            for member_name, member in inspect.getmembers(self):
                if has_annotation(member, Annotation.MIDDLEWARE):
                    self._client.middleware.add(member)
                elif has_operation(member):
                    bound_operation_func: Callable = self._client.bind(member)
                    bound_operation_method: Callable = bound_operation_func.__get__(
                        self
                    )

                    bound_operation: Operation = get_operation(bound_operation_method)

                    bound_operation.func = bound_operation_method
                    bound_operation.middleware = Middleware()

                    bound_operation.middleware.add_all(self._client.middleware.record)

                    setattr(self, member_name, bound_operation_method)

        attrs["_spec"] = ClientSpecification()
        attrs["__init__"] = __init__

        typ: type = super().__new__(mcs, name, bases, attrs)

        return typ


class Service(metaclass=ServiceMeta):
    _client: Client

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"
