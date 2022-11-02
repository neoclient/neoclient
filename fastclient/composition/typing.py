from typing import Protocol, TypeVar, runtime_checkable

from typing_extensions import ParamSpec

from ..models import RequestOptions

T = TypeVar("T", contravariant=True)

PS = ParamSpec("PS")


@runtime_checkable
class RequestConsumer(Protocol):
    def __call__(self, request: RequestOptions, /) -> None:
        ...


class RequestConsumerFactory(Protocol[PS]):
    def __call__(self, *args: PS.args, **kwargs: PS.kwargs) -> RequestConsumer:
        ...