from dataclasses import dataclass
from typing import Any, Callable, Optional, Protocol, Sequence, TypeVar

from typing_extensions import ParamSpec

from .client import NeoClient
from .enums import HTTPMethod

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


put: OperationDecorator = MethodOperationDecorator(HTTPMethod.PUT)
get: OperationDecorator = MethodOperationDecorator(HTTPMethod.GET)
post: OperationDecorator = MethodOperationDecorator(HTTPMethod.POST)
head: OperationDecorator = MethodOperationDecorator(HTTPMethod.HEAD)
patch: OperationDecorator = MethodOperationDecorator(HTTPMethod.PATCH)
delete: OperationDecorator = MethodOperationDecorator(HTTPMethod.DELETE)
options: OperationDecorator = MethodOperationDecorator(HTTPMethod.OPTIONS)
