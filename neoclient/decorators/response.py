from dataclasses import dataclass
from typing import Sequence, Type

from ..errors import CompositionError
from ..operation import Operation, get_operation
from ..services import Service
from ..specification import ClientSpecification
from ..typing import Dependency
from .api import CS, CommonDecorator

__all__: Sequence[str] = ("response",)


@dataclass
class ResponseDecorator(CommonDecorator):
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
