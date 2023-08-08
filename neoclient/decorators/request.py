from dataclasses import dataclass
from typing import Any, Callable, Optional, Sequence, Type, TypeVar

from typing_extensions import ParamSpec

from ..client import Client
from ..enums import HTTPMethod
from ..service import Service
from ..typing import Dependency
from .common import request_depends

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

CS = TypeVar("CS", Callable, Type[Service])

PS = ParamSpec("PS")
RT = TypeVar("RT")


@dataclass
class MethodOperationDecorator:
    method: str

    def __call__(
        self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
    ) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
        return Client().request(self.method, endpoint, response=response)


@dataclass
class RequestDecorator:
    method: str
    endpoint: str
    response: Optional[Dependency]

    def __init__(
        self,
        method: str,
        endpoint: str,
        /,
        *,
        response: Optional[Dependency] = None,
    ) -> None:
        self.method = method
        self.endpoint = endpoint
        self.response = response

    def __call__(self, func: Callable[PS, RT], /) -> Callable[PS, RT]:
        return Client().request(self.method, self.endpoint, response=self.response)(
            func
        )

    @staticmethod
    def depends(*dependencies: Dependency) -> Callable[[CS], CS]:
        return request_depends(*dependencies)


request: Type[RequestDecorator] = RequestDecorator

put: MethodOperationDecorator = MethodOperationDecorator(HTTPMethod.PUT)
get: MethodOperationDecorator = MethodOperationDecorator(HTTPMethod.GET)
post: MethodOperationDecorator = MethodOperationDecorator(HTTPMethod.POST)
head: MethodOperationDecorator = MethodOperationDecorator(HTTPMethod.HEAD)
patch: MethodOperationDecorator = MethodOperationDecorator(HTTPMethod.PATCH)
delete: MethodOperationDecorator = MethodOperationDecorator(HTTPMethod.DELETE)
options: MethodOperationDecorator = MethodOperationDecorator(HTTPMethod.OPTIONS)
