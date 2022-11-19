from dataclasses import dataclass
from typing import Any, Callable, Optional, Protocol, Sequence, TypeVar

from typing_extensions import ParamSpec

from .client import FastClient
from .enums import HttpMethod
from .operation import CallableWithOperation

__all__: Sequence[str] = (
    "request",
    "put",
    "get",
    "post",
    "head",
    "patch",
    "delete",
    "options",
)

PS = ParamSpec("PS")
RT = TypeVar("RT")


class OperationDecorator(Protocol):
    def __call__(
        self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
    ) -> Callable[[Callable[PS, RT]], CallableWithOperation[PS, RT]]:
        ...


@dataclass
class MethodOperationDecorator(OperationDecorator):
    method: str

    def __call__(
        self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
    ) -> Callable[[Callable[PS, RT]], CallableWithOperation[PS, RT]]:
        return FastClient().request(self.method, endpoint, response=response)


def request(
    method: str, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
) -> Callable[[Callable[PS, RT]], CallableWithOperation[PS, RT]]:
    return MethodOperationDecorator(method)(endpoint, response=response)


put: OperationDecorator = MethodOperationDecorator(HttpMethod.PUT)
get: OperationDecorator = MethodOperationDecorator(HttpMethod.GET)
post: OperationDecorator = MethodOperationDecorator(HttpMethod.POST)
head: OperationDecorator = MethodOperationDecorator(HttpMethod.HEAD)
patch: OperationDecorator = MethodOperationDecorator(HttpMethod.PATCH)
delete: OperationDecorator = MethodOperationDecorator(HttpMethod.DELETE)
options: OperationDecorator = MethodOperationDecorator(HttpMethod.OPTIONS)
