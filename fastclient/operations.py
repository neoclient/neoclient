import dataclasses
import inspect
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Optional,
    TypeVar,
)

import httpx
import param
import param.models
import pydantic
from httpx import Client, Response
from pydantic import BaseModel
from typing_extensions import ParamSpec

from . import utils
from .errors import NotAnOperation
from .models import OperationSpecification, RequestOptions
from .populaters import compose_func
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
        arguments: Dict[str, Any] = self._get_arguments(*args, **kwargs)

        request_options: RequestOptions = self.build_request_options(arguments)

        request: httpx.Request = request_options.build_request(self.client)

        return_annotation: Any = inspect.signature(self.func).return_annotation

        if return_annotation is RequestOptions:
            return request_options
        if return_annotation is httpx.Request:
            return request

        client: Client = self.client if self.client is not None else Client()

        response: Response = client.send(request)

        if self.specification.response is not None:
            request_options_with_unpopulated_url = dataclasses.replace(request_options, url=self.specification.request.url)
            
            # return resolve_func(response, self.specification.response, request=request_options_with_unpopulated_url, target_type=return_annotation)
            # return resolve_func(response, self.specification.response)
            return resolve_func(request_options_with_unpopulated_url, response, self.specification.response, cached_dependencies={})

        if return_annotation is inspect._empty:
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

    def build_request_options(self, arguments: Dict[str, Any], /) -> RequestOptions:
        request: RequestOptions = self.specification.request.merge(
            RequestOptions(
                method=self.specification.request.method,
                url=self.specification.request.url,
            )
        )

        compose_func(request, self.func, arguments)

        return request

    def _get_arguments(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        arguments: Dict[str, Any] = utils.bind_arguments(self.func, args, kwargs)

        # TODO: Find a better fix for instance methods
        if arguments and list(arguments)[0] == "self":
            arguments.pop("self")

        argument_name: str
        argument: Any
        for argument_name, argument in arguments.items():
            if isinstance(argument, param.models.Param):
                if not argument.has_default():
                    raise ValueError(
                        f"{self.func.__name__}() missing argument: {argument_name!r}"
                    )

                arguments[argument_name] = argument.get_default()

        return arguments
