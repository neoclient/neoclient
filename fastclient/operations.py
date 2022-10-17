import dataclasses
import inspect
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Generic,
    Optional,
    TypeVar,
)

import httpx
import pydantic
from httpx import Client, Response
from pydantic import BaseModel
from typing_extensions import ParamSpec

from .errors import NotAnOperation
from .models import OperationSpecification, RequestOptions
from .composers import compose_func
from .resolvers import resolve_func

PS = ParamSpec("PS")
RT = TypeVar("RT")


def get_operation(obj: Any, /) -> "Operation":
    if not has_operation(obj):
        raise NotAnOperation(f"{obj!r} is not an operation")

    return getattr(obj, "operation")


def has_operation(obj: Any, /) -> bool:
    return hasattr(obj, "operation")


def set_operation(obj: Any, operation: "Operation", /) -> None:
    setattr(obj, "operation", operation)


def del_operation(obj: Any, /) -> None:
    delattr(obj, "operation")


@dataclass
class Operation(Generic[PS, RT]):
    func: Callable[PS, RT]
    specification: OperationSpecification
    client: Optional[Client]

    def __call__(self, *args: PS.args, **kwargs: PS.kwargs) -> Any:
        request_options: RequestOptions = self.specification.request.merge(
            RequestOptions(
                method=self.specification.request.method,
                url=self.specification.request.url,
            )
        )

        compose_func(request_options, self.func, args, kwargs)

        request: httpx.Request = request_options.build_request(self.client)

        return_annotation: Any = inspect.signature(self.func).return_annotation

        if return_annotation is RequestOptions:
            return request_options
        if return_annotation is httpx.Request:
            return request

        client: Client = self.client if self.client is not None else Client()

        response: Response = client.send(request)

        if self.specification.response is not None:
            request_options_with_unpopulated_url = dataclasses.replace(
                request_options, url=self.specification.request.url
            )

            return resolve_func(
                request_options_with_unpopulated_url,
                response,
                self.specification.response,
                cached_dependencies={},
            )

        if return_annotation is inspect.Parameter.empty:
            return response.json()
        if return_annotation is None:
            return None
        if return_annotation is Response:
            return response
        if isinstance(return_annotation, type) and issubclass(
            return_annotation, BaseModel
        ):
            return return_annotation.parse_obj(response.json())

        return pydantic.parse_raw_as(return_annotation, response.text)
