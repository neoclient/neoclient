import functools
import inspect
from dataclasses import dataclass, field
from json import JSONDecodeError
from typing import Any, Callable, Generic, Optional, Sequence, TypeVar

import pydantic
from httpx import Client, Request, Response
from pydantic import BaseModel
from typing_extensions import ParamSpec

from .composition import compose
from .errors import NotAnOperationError
from .middleware import Middleware
from .models import OperationSpecification, RequestOptions
from .resolution import resolve

__all__: Sequence[str] = (
    "set_operation",
    "has_operation",
    "get_operation",
    "Operation",
)

PS = ParamSpec("PS")
RT = TypeVar("RT", covariant=True)

ATTRIBUTE_OPERATION: str = "operation"


def set_operation(func: Callable, operation: "Operation", /) -> None:
    setattr(func, ATTRIBUTE_OPERATION, operation)


def has_operation(func: Callable, /) -> bool:
    return hasattr(func, ATTRIBUTE_OPERATION)


def get_operation(func: Callable, /) -> "Operation":
    operation: Optional[Operation] = getattr(func, ATTRIBUTE_OPERATION, None)

    if operation is None:
        raise NotAnOperationError(f"{func!r} is not an operation")

    return operation


@dataclass
class Operation(Generic[PS, RT]):
    func: Callable[PS, RT]
    specification: OperationSpecification
    client: Optional[Client]
    middleware: Middleware = field(default_factory=Middleware)

    def __call__(self, *args: PS.args, **kwargs: PS.kwargs) -> Any:
        request_options: RequestOptions = self.specification.request.merge(
            RequestOptions(
                method=self.specification.request.method,
                url=self.specification.request.url,
            )
        )

        compose(self.func, request_options, args, kwargs)

        request: Request = request_options.build_request(self.client)

        return_annotation: Any = inspect.signature(self.func).return_annotation

        if return_annotation is RequestOptions:
            return request_options
        if return_annotation is Request:
            return request

        client: Client = self.client if self.client is not None else Client()

        middleware: Middleware = Middleware()

        middleware.record.extend(self.specification.middleware.record)
        middleware.record.extend(self.middleware.record)

        @middleware.compose
        def send_request(request: Request, /) -> Response:
            return client.send(request)

        response: Response = send_request(request)

        if self.specification.response is not None:
            return resolve(self.specification.response, response)

        if return_annotation is inspect.Parameter.empty:
            try:
                return response.json()
            except JSONDecodeError:
                return response.text
        if return_annotation is None:
            return None
        if return_annotation is Response:
            return response
        if isinstance(return_annotation, type) and issubclass(
            return_annotation, BaseModel
        ):
            return return_annotation.parse_obj(response.json())

        return pydantic.parse_raw_as(return_annotation, response.text)

    @property
    def wrapper(self) -> Callable[PS, RT]:
        @functools.wraps(self.func)
        def wrapper(*args: PS.args, **kwargs: PS.kwargs) -> RT:
            if inspect.ismethod(self.func):
                # Read off `self` or `cls`
                _, *args = args  # type: ignore

            return self(*args, **kwargs)

        set_operation(wrapper, self)

        return wrapper
