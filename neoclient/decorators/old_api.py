from abc import abstractmethod
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Protocol,
    Sequence,
    Type,
    TypeVar,
    Union,
    runtime_checkable,
)

from ..errors import CompositionError
from ..models import ClientOptions, RequestOptions
from ..operation import Operation, get_operation
from ..services import Service
from ..specification import ClientSpecification
from ..typing import Consumer, SupportsConsumeClient, SupportsConsumeRequest

__all__: Sequence[str] = (
    # Protocols
    "OperationDecorator",
    "ServiceDecorator",
    "CommonDecorator",
    # Wrappers
    "ConsumerDecorator",
    "OperationConsumerDecorator",
    "ServiceConsumerDecorator",
)

C = TypeVar("C", bound=Callable[..., Any])
S = TypeVar("S", bound=Type[Service])
CS = TypeVar("CS", Callable[..., Any], Type[Service])


@runtime_checkable
class SupportsConsumeClientSpecification(Protocol):
    @abstractmethod
    def consume_client_spec(self, client_specification: ClientSpecification, /) -> None:
        ...


@runtime_checkable
class SupportsConsumeOperation(Protocol):
    @abstractmethod
    def consume_operation(self, operation: Operation, /) -> None:
        ...


class ClientSpecificationConsumer(Consumer[ClientSpecification], Protocol):
    pass


class OperationConsumer(Consumer[Operation], Protocol):
    pass


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
    consumer: Union[
        SupportsConsumeOperation,
        SupportsConsumeRequest,
        SupportsConsumeClient,
    ]

    def __call__(self, target: C, /) -> C:
        if not callable(target):
            raise CompositionError(f"Target of unsupported type {type(target)}")

        operation: Operation = get_operation(target)

        if isinstance(self.consumer, SupportsConsumeOperation):
            self.consumer.consume_operation(operation)
        elif isinstance(self.consumer, SupportsConsumeRequest):
            pre_request: RequestOptions = operation.request_options

            self.consumer.consume_request(pre_request)
        elif isinstance(self.consumer, SupportsConsumeClient):
            client_options: ClientOptions = operation.client_options

            self.consumer.consume_client(client_options)
        else:
            raise CompositionError(
                f"Consumer {self.consumer} does not support consuming a request or client"
            )

        return target


@dataclass
class ServiceConsumerDecorator(ServiceDecorator):
    consumer: Union[SupportsConsumeClientSpecification, SupportsConsumeClient]

    def __call__(self, target: S, /) -> S:
        if not isinstance(target, type):
            raise CompositionError(f"Target of unsupported type {type(target)}")

        if not issubclass(target, Service):
            raise CompositionError(f"Target class is not a subclass of {Service}")

        specification: ClientSpecification = target._spec
        options: ClientOptions = specification.options

        if isinstance(self.consumer, SupportsConsumeClientSpecification):
            self.consumer.consume_client_spec(specification)
        elif isinstance(self.consumer, SupportsConsumeClient):
            self.consumer.consume_client(options)
        else:
            raise CompositionError(
                f"Consumer {self.consumer} does not support consuming client specification or options"
            )

        return target


@dataclass
class ConsumerDecorator(CommonDecorator):
    consumer: Union[
        SupportsConsumeOperation,
        SupportsConsumeRequest,
        SupportsConsumeClientSpecification,
        SupportsConsumeClient,
    ]

    def __call__(self, target: CS, /) -> CS:
        if isinstance(target, type):
            if not isinstance(
                self.consumer,
                (SupportsConsumeClientSpecification, SupportsConsumeClient),
            ):
                raise CompositionError(
                    f"Consumer {type(self.consumer).__name__!r} does not support consumption"
                    f" of type {Service}"
                )

            return ServiceConsumerDecorator(self.consumer)(target)
        elif callable(target):
            if not isinstance(
                self.consumer,
                (
                    SupportsConsumeOperation,
                    SupportsConsumeRequest,
                    SupportsConsumeClient,
                ),
            ):
                raise CompositionError(
                    f"Consumer {type(self.consumer).__name__!r} does not support consuming"
                    f" target of type {type(target)}"
                )

            return OperationConsumerDecorator(self.consumer)(target)
        else:
            raise CompositionError(f"Target of unsupported type {type(target)}")
