import inspect
from typing import Any, Callable, Dict, Tuple, Type

from .client import NeoClient
from .operation import Operation, get_operation, has_operation


class ServiceMeta(type):
    def __new__(
        cls: Type["ServiceMeta"], name: str, bases: Tuple[type], attrs: Dict[str, Any]
    ) -> type:
        def __init__(self) -> None:
            client: NeoClient = NeoClient()

            member_name: str
            member: Any
            for member_name, member in inspect.getmembers(typ):
                if not has_operation(member):
                    continue

                bound_operation_func: Callable = client.bind(member)
                bound_operation_method: Callable = bound_operation_func.__get__(self)

                operation: Operation = get_operation(bound_operation_method)

                operation.func = bound_operation_method

                setattr(self, member_name, bound_operation_method)

        attrs["__init__"] = __init__

        typ: type = super().__new__(cls, name, bases, attrs)

        return typ

    # def __init__(
    #     cls: type, name: str, bases: Tuple[type], attrs: Dict[str, Any]
    # ) -> None:
    #     print("ServiceMeta.__init__:", dict(cls=cls, name=name, bases=bases, attrs=attrs))


class Service(metaclass=ServiceMeta):
    def __repr__(self) -> str:
        return f"{type(self).__name__}()"
