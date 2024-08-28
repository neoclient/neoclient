from abc import abstractmethod
from typing import Protocol, runtime_checkable

from neoclient.decorators.api import ConsumerDecorator
from neoclient.models import PreRequest


# TODO: Resolve name collision with neoclient.typing.RequestConsumer
@runtime_checkable
class RequestConsumer(Protocol):
    @abstractmethod
    def consume_request(self, request: PreRequest, /) -> None:
        raise NotImplementedError


# TODO: Support all consumers (for now just supports request consumers)
# TODO: Type me
def build_decorator(consumer: RequestConsumer, /):
    return ConsumerDecorator(consumer)
