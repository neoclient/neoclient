from typing import Protocol, TypeVar, runtime_checkable

from typing_extensions import ParamSpec

from ..models import RequestOptions
from ..operations import CallableWithOperation

C = TypeVar("C", bound=CallableWithOperation)
T = TypeVar("T", contravariant=True)

PS = ParamSpec("PS")


class Decorator(Protocol):
    def __call__(self, func: C, /) -> C:
        ...


@runtime_checkable
class RequestConsumer(Protocol):
    def __call__(self, request: RequestOptions, /) -> None:
        ...


class RequestConsumerFactory(Protocol[PS]):
    def __call__(self, *args: PS.args, **kwargs: PS.kwargs) -> RequestConsumer:
        ...
