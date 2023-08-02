from dataclasses import dataclass
from typing import Callable, Sequence, Type, TypeVar, Union

from ..errors import CompositionError
from ..models import ClientOptions, PreRequest
from ..operation import get_operation
from ..service import Service
from ..typing import Decorator, SupportsConsumeClient, SupportsConsumeRequest

__all__: Sequence[str] = ("ConsumerDecorator",)

T = TypeVar("T", Callable, Type[Service])


@dataclass
class ConsumerDecorator(Decorator[T]):
    consumer: Union[SupportsConsumeRequest, SupportsConsumeClient]

    def __call__(self, target: T, /) -> T:
        if isinstance(target, type):
            if not issubclass(target, Service):
                raise CompositionError(f"Target class is not a subclass of {Service}")

            if not isinstance(self.consumer, SupportsConsumeClient):
                raise CompositionError(
                    f"Consumer {type(self.consumer).__name__!r} does not support consumption"
                    f" of type {Service}"
                )

            client: ClientOptions = target._spec.options

            self.consumer.consume_client(client)
        elif callable(target):
            if isinstance(self.consumer, SupportsConsumeRequest):
                pre_request: PreRequest = get_operation(target).request_options

                self.consumer.consume_request(pre_request)
            else:
                client_options: ClientOptions = get_operation(target).client_options

                self.consumer.consume_client(client_options)
        else:
            raise CompositionError(f"Target of unsupported type {type(target)}")

        return target
