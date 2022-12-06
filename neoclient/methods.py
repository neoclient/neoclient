from dataclasses import dataclass
from typing import Any, Callable, Optional, Protocol, Sequence, TypeVar

from typing_extensions import ParamSpec

from .client import NeoClient
from .enums import HttpMethod

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
    ) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
        ...


@dataclass
class MethodOperationDecorator(OperationDecorator):
    method: str

    def __call__(
        self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
    ) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
        return NeoClient().request(self.method, endpoint, response=response)


def request(
    method: str, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    return MethodOperationDecorator(method)(endpoint, response=response)


put: OperationDecorator = MethodOperationDecorator(HttpMethod.PUT)
get: OperationDecorator = MethodOperationDecorator(HttpMethod.GET)
post: OperationDecorator = MethodOperationDecorator(HttpMethod.POST)
head: OperationDecorator = MethodOperationDecorator(HttpMethod.HEAD)
patch: OperationDecorator = MethodOperationDecorator(HttpMethod.PATCH)
delete: OperationDecorator = MethodOperationDecorator(HttpMethod.DELETE)
options: OperationDecorator = MethodOperationDecorator(HttpMethod.OPTIONS)
