from dataclasses import dataclass
import inspect
from typing import Any, Callable, Dict, Generic, Optional, TypeVar
from typing_extensions import ParamSpec
import urllib.parse

from arguments import Arguments
import param
import pydantic
from pydantic import BaseModel
import fastapi.encoders
import httpx
from httpx import Response, Client

from . import api
from .models import OperationSpecification, RequestOptions
from .enums import ParamType
from .params import Param, Params

PS = ParamSpec("PS")
RT = TypeVar("RT")


def get_operation(obj: Any, /) -> Optional["Operation"]:
    return getattr(obj, "operation", None)


@dataclass
class Operation(Generic[PS, RT]):
    func: Callable[PS, RT]
    specification: OperationSpecification
    client: Optional[Client]

    def __call__(self, *args: PS.args, **kwargs: PS.kwargs) -> Any:
        arguments: Dict[str, Any] = self._get_arguments(*args, **kwargs)

        new_request_options: RequestOptions = self.build_request_options(arguments)
        request_options: RequestOptions = self.specification.request.merge(new_request_options)

        request: httpx.Request = request_options.build_request(self.client)

        return_annotation: Any = self.response_type

        if return_annotation is RequestOptions:
            return request_options
        if return_annotation is httpx.Request:
            return request

        client: Client = self.client if self.client is not None else Client()

        response: Response = client.send(request)

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

    def build_request_options(self, arguments: Dict[str, Any], /) -> RequestOptions:
        query_params: httpx.QueryParams = httpx.QueryParams()
        path_params: Dict[str, Any] = {}
        headers: httpx.Headers = httpx.Headers()
        cookies: httpx.Cookies = httpx.Cookies()
        body_params: Dict[str, Any] = {}

        parameter: str
        field: Param
        for parameter, field in self.params.items():
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

                if field.type is ParamType.QUERY:
                    query_params = query_params.set(field_name, value)
                elif field.type is ParamType.HEADER:
                    headers[field_name] = value
                elif field.type is ParamType.PATH:
                    path_params[field_name] = value
                elif field.type is ParamType.COOKIE:
                    cookies[field_name] = value
                elif field.type is ParamType.BODY:
                    body_params[field_name] = value
                else:
                    raise Exception(f"Unknown ParamType: {field.type!r}")
            elif isinstance(field, Params):
                if field.type is ParamType.QUERY:
                    query_params = query_params.merge(value)
                elif field.type is ParamType.HEADER:
                    headers.update(value)
                elif field.type is ParamType.COOKIE:
                    cookies.update(value)
            else:
                raise Exception(f"Unknown field type: {field}")

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

        return RequestOptions(
            method=self.specification.request.method,
            url=urllib.parse.unquote(str(self.specification.request.url)).format(**path_params),
            params=query_params,
            headers=headers,
            cookies=cookies,
            json=json,
        )

    def _is_method(self) -> bool:
        return bool(self.params and list(self.params)[0] == "self")

    def _get_arguments(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        arguments: Dict[str, Any] = Arguments(*args, **kwargs).bind(self.func).asdict()

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

        return arguments

    @property
    def params(self) -> Dict[str, Param]:
        parameters: Dict[str, param.Parameter] = api.get_params(
            self.func, request=self.specification.request
        )
        
        return {
            parameter.name: parameter.spec for parameter in parameters.values()
        }

    @property
    def response_type(self) -> Any:
        return inspect.signature(self.func).return_annotation