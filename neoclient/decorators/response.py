from dataclasses import dataclass
from typing import Sequence

from ..operation import Operation
from ..specification import ClientSpecification
from ..typing import Dependency
from .old_api import (
    CommonDecorator,
    ConsumerDecorator,
    SupportsConsumeClientSpecification,
    SupportsConsumeOperation,
)

__all__: Sequence[str] = ("response",)


@dataclass
class ResponseConsumer(SupportsConsumeOperation, SupportsConsumeClientSpecification):
    dependency: Dependency

    def consume_operation(self, operation: Operation, /) -> None:
        operation.response = self.dependency

    def consume_client_spec(self, client_specification: ClientSpecification, /) -> None:
        client_specification.default_response = self.dependency


def response(dependency: Dependency, /) -> CommonDecorator:
    return ConsumerDecorator(ResponseConsumer(dependency))
