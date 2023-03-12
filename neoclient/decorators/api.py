from dataclasses import dataclass
from typing import Callable, Sequence, Type, TypeVar

from ..consumers import Consumer
from ..errors import CompositionError
from ..models import ClientOptions, PreRequest
from ..operation import get_operation
from ..service import Service
from ..typing import Decorator

__all__: Sequence[str] = (
    "ConsumerDecorator",
)

T = TypeVar("T", Callable, Type[Service])


@dataclass
class ConsumerDecorator(Decorator[T]):
    consumer: Consumer

    def __call__(self, target: T, /) -> T:
        if isinstance(target, type):
            if not issubclass(target, Service):
                raise CompositionError(f"Target class is not a subclass of {Service}")

            client: ClientOptions = target._spec.options

            self.consumer.consume_client(client)
        elif callable(target):
            request: PreRequest = get_operation(target).specification.request

            self.consumer.consume_request(request)
        else:
            raise CompositionError(f"Target of unsupported type {type(target)}")

        return target
