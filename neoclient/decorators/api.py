from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Protocol, Sequence, Type, TypeVar, Union

from ..errors import CompositionError
from ..models import ClientOptions, PreRequest
from ..operation import Operation, get_operation
from ..services import Service
from ..specification import ClientSpecification
from ..typing import Dependency, SupportsConsumeClient, SupportsConsumeRequest

__all__: Sequence[str] = (
    "ConsumerDecorator",
    "OperationConsumerDecorator",
    "ServiceConsumerDecorator",
    "RequestDependsDecorator",
)

C = TypeVar("C", bound=Callable[..., Any])
S = TypeVar("S", bound=Type[Service])
CS = TypeVar("CS", Callable[..., Any], Type[Service])


class OperationDecorator(Protocol):
    @abstractmethod
    def __call__(self, target: C, /) -> C:
        raise NotImplementedError


class ServiceDecorator(Protocol):
    @abstractmethod
    def __call__(self, target: S, /) -> S:
        raise NotImplementedError


class CommonDecorator(Protocol):
    @abstractmethod
    def __call__(self, target: CS, /) -> CS:
        raise NotImplementedError


@dataclass
class OperationConsumerDecorator(OperationDecorator):
    consumer: Union[SupportsConsumeRequest, SupportsConsumeClient]

    def __call__(self, target: C, /) -> C:
        if not callable(target):
            raise CompositionError(f"Target of unsupported type {type(target)}")

        if isinstance(self.consumer, SupportsConsumeRequest):
            pre_request: PreRequest = get_operation(target).pre_request

            self.consumer.consume_request(pre_request)
        else:
            client_options: ClientOptions = get_operation(target).client_options

            self.consumer.consume_client(client_options)

        return target


@dataclass
class ServiceConsumerDecorator(ServiceDecorator):
    consumer: SupportsConsumeClient

    def __call__(self, target: S, /) -> S:
        if not isinstance(target, type):
            raise CompositionError(f"Target of unsupported type {type(target)}")

        if not issubclass(target, Service):
            raise CompositionError(f"Target class is not a subclass of {Service}")

        client: ClientOptions = target._spec.options

        self.consumer.consume_client(client)

        return target


@dataclass
class ConsumerDecorator(CommonDecorator):
    consumer: Union[SupportsConsumeRequest, SupportsConsumeClient]

    def __call__(self, target: CS, /) -> CS:
        if isinstance(target, type):
            if not isinstance(self.consumer, SupportsConsumeClient):
                raise CompositionError(
                    f"Consumer {type(self.consumer).__name__!r} does not support consumption"
                    f" of type {Service}"
                )

            return ServiceConsumerDecorator(self.consumer)(target)
        elif callable(target):
            return OperationConsumerDecorator(self.consumer)(target)
        else:
            raise CompositionError(f"Target of unsupported type {type(target)}")


@dataclass
class RequestDependsDecorator(CommonDecorator):
    dependencies: Sequence[Dependency]

    def __init__(self, *dependencies: Dependency) -> None:
        self.dependencies = dependencies

    def __call__(self, target: CS, /) -> CS:
        if isinstance(target, type):
            if not issubclass(target, Service):
                raise CompositionError(f"Target class is not a subclass of {Service}")

            client_specification: ClientSpecification = target._spec

            client_specification.request_dependencies.extend(self.dependencies)
        elif callable(target):
            operation: Operation = get_operation(target)

            operation.request_dependencies.extend(self.dependencies)
        else:
            raise CompositionError(f"Target of unsupported type {type(target)}")

        return target
