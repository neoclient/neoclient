from abc import ABC, abstractmethod
from dataclasses import dataclass
import inspect
from typing import Any, Callable, Dict, Generic, Optional, TypeVar
from typing_extensions import ParamSpec

from arguments import Arguments
import param
import pydantic
from pydantic import BaseModel
import fastapi.encoders
import httpx
from httpx import Response, Client

from . import api
from .errors import UnboundOperationException
from .models import OperationSpecification, RequestOptions
from .enums import ParamType
from .params import Param, Params

PS = ParamSpec("PS")
RT = TypeVar("RT")


def get_operation(obj: Any, /) -> Optional["Operation"]:
    return getattr(obj, "operation", None)


@dataclass
class Operation(ABC, Generic[PS, RT]):
    func: Callable[PS, RT]
    specification: OperationSpecification

    @abstractmethod
    def __call__(self, *args: PS.args, **kwargs: PS.kwargs) -> Any:
        raise NotImplementedError


@dataclass
class BoundOperation(Operation[PS, RT]):
    client: Client

    def __call__(self, *args: PS.args, **kwargs: PS.kwargs) -> Any:
        arguments: Dict[str, Any]

        # TODO: Find a better fix for instance methods!
        if self._is_method():
            arguments = Arguments(None, *args, **kwargs).bind(self.func).asdict()
        else:
            arguments = Arguments(*args, **kwargs).bind(self.func).asdict()

        argument_name: str
        argument: Any
        for argument_name, argument in arguments.items():
            if not isinstance(argument, Param):
                continue

            if not argument.has_default():
                raise ValueError(
                    f"{self.func.__name__}() missing argument: {argument_name!r}"
                )

            arguments[argument_name] = argument.default

        destinations: Dict[ParamType, Dict[str, Any]] = {}

        parameter: str
        field: Param
        for parameter, field in self.specification.params.items():
            value: Any = arguments[parameter]

            if isinstance(field, Param):
                field_name: str = (
                    field.alias
                    if field.alias is not None
                    else field.generate_alias(parameter)
                )

                # The field is not required, it can be omitted
                if value is None and not field.required:
                    continue

                destinations.setdefault(field.type, {})[field_name] = value
            elif isinstance(field, Params):
                destinations.setdefault(field.type, {}).update(value)
            else:
                raise Exception(f"Unknown field type: {field}")

        body_params: Dict[str, Any] = destinations.get(ParamType.BODY, {})

        json: Any = None

        # If there's only one body param, make it the entire JSON request body
        if len(body_params) == 1:
            json = fastapi.encoders.jsonable_encoder(list(body_params.values())[0])
        # If there are multiple body params, construct a multi-level dict
        # of each body parameter. E.g. (user: User, item: Item) -> {"user": ..., "item": ...}
        elif body_params:
            json = {
                key: fastapi.encoders.jsonable_encoder(val)
                for key, val in body_params.items()
            }

        method: str = self.specification.request.method
        url: str = str(self.specification.request.url).format(
            **destinations.get(ParamType.PATH, {})
        )
        params: dict = {
            **self.specification.request.params,
            **destinations.get(ParamType.QUERY, {}),
        }
        headers: dict = {
            **self.specification.request.headers,
            **destinations.get(ParamType.HEADER, {}),
        }
        cookies: dict = {
            **self.specification.request.cookies,
            **destinations.get(ParamType.COOKIE, {}),
        }

        request: RequestOptions = RequestOptions(
            method=method,
            url=url,
            params=params,
            headers=headers,
            cookies=cookies,
            json=json,
        )

        httpx_request: httpx.Request = self.client.build_request(
            method=method,
            url=url,
            params=params,
            headers=headers,
            cookies=cookies,
            json=json,
        )

        return_annotation: Any = self.specification.response_type

        if return_annotation is RequestOptions:
            return request
        if return_annotation is httpx.Request:
            return httpx_request

        response: Response = self.client.send(httpx_request)

        if self.specification.response is not None:
            response_params: Dict[str, param.Parameter] = api.get_params(
                self.specification.response, request=self.specification.request
            )
            response_arguments: Arguments = api.get_response_arguments(
                response, response_params, self.specification.request
            )

            return response_arguments.call(self.specification.response)

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

    def _is_method(self) -> bool:
        return bool(
            self.specification.params and list(self.specification.params)[0] == "self"
        )


class UnboundOperation(Operation[PS, RT]):
    def __call__(self, *args: PS.args, **kwargs: PS.kwargs) -> Any:
        raise UnboundOperationException(
            f"Operation `{self.func.__name__}` has not been bound to a client"
        )

    def bind(self, client: Client, /) -> BoundOperation:
        return BoundOperation(
            func=self.func, specification=self.specification, client=client
        )
