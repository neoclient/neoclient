from typing import Callable, Protocol, TypeVar
from typing_extensions import ParamSpec

from ..models import RequestOptions

C = TypeVar("C", bound=Callable)
T = TypeVar("T", contravariant=True)

PS = ParamSpec("PS")


class Decorator(Protocol):
    def __call__(self, func: C, /) -> C:
        ...


class RequestConsumer(Protocol):
    def __call__(self, request: RequestOptions, /) -> None:
        ...


class RequestConsumerFactory(Protocol[PS]):
    def __call__(self, *args: PS.args, **kwargs: PS.kwargs) -> RequestConsumer:
        ...
