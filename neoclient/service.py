import inspect
from typing import Any, Callable, Dict, Tuple, Type

from annotate.utils import has_annotation

from .client import Client
from .enums import Sentinel
from .models import ClientOptions
from .operation import Operation, get_operation, has_operation


class ServiceMeta(type):
    def __new__(
        cls: Type["ServiceMeta"], name: str, bases: Tuple[type], attrs: Dict[str, Any]
    ) -> type:
        def __init__(self) -> None:
            self._client = Client(client=self._opts.build())

            member_name: str
            member: Any
            for member_name, member in inspect.getmembers(self):
                if has_annotation(member, Sentinel.MIDDLEWARE):
                    self._client.middleware.add(member)
                elif has_operation(member):
                    bound_operation_func: Callable = self._client.bind(member)
                    bound_operation_method: Callable = bound_operation_func.__get__(self)

                    bound_operation: Operation = get_operation(bound_operation_method)

                    bound_operation.func = bound_operation_method
                    bound_operation.middleware = self._client.middleware

                    setattr(self, member_name, bound_operation_method)

        attrs["_opts"] = ClientOptions()
        attrs["__init__"] = __init__

        typ: type = super().__new__(cls, name, bases, attrs)

        return typ


class Service(metaclass=ServiceMeta):
    _opts: ClientOptions
    _client: Client

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"
