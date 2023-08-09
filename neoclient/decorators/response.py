from dataclasses import dataclass
from typing import Callable, Sequence, Type, TypeVar

from ..errors import CompositionError
from ..operation import Operation, get_operation
from ..service import Service
from ..specification import ClientSpecification
from ..typing import Dependency

__all__: Sequence[str] = ("response",)

CS = TypeVar("CS", Callable, Type[Service])


@dataclass
class ResponseDecorator:
    dependency: Dependency

    def __call__(self, target: CS, /) -> CS:
        if isinstance(target, type):
            if not issubclass(target, Service):
                raise CompositionError(f"Target class is not a subclass of {Service}")

            client_specification: ClientSpecification = target._spec

            client_specification.default_response = self.dependency
        elif callable(target):
            operation: Operation = get_operation(target)

            operation.response = self.dependency
        else:
            raise CompositionError(f"Target of unsupported type {type(target)}")

        return target


response: Type[ResponseDecorator] = ResponseDecorator
