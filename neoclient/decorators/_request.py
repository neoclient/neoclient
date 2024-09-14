from dataclasses import dataclass
from typing import Callable, Optional, Sequence, TypeVar

from typing_extensions import ParamSpec

from ..client import Client
from ..enums import HTTPMethod
from ..typing import Dependency

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


def request(
    method: str,
    endpoint: str,
    /,
    *,
    response: Optional[Dependency] = None,
) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
    return Client().request(method, endpoint, response=response)


@dataclass
class MethodRequestDecorator:
    method: str

    def __call__(
        self,
        endpoint: str,
        /,
        *,
        response: Optional[Dependency] = None,
    ) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
        return request(self.method, endpoint, response=response)


put: MethodRequestDecorator = MethodRequestDecorator(HTTPMethod.PUT)
get: MethodRequestDecorator = MethodRequestDecorator(HTTPMethod.GET)
post: MethodRequestDecorator = MethodRequestDecorator(HTTPMethod.POST)
head: MethodRequestDecorator = MethodRequestDecorator(HTTPMethod.HEAD)
patch: MethodRequestDecorator = MethodRequestDecorator(HTTPMethod.PATCH)
delete: MethodRequestDecorator = MethodRequestDecorator(HTTPMethod.DELETE)
options: MethodRequestDecorator = MethodRequestDecorator(HTTPMethod.OPTIONS)
