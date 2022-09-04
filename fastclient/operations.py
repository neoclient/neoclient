import inspect
import urllib.parse
from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, Optional, Set, TypeVar

import fastapi.encoders
import httpx
import param
import pydantic
from httpx import Client, Response
from pydantic import BaseModel
from typing_extensions import ParamSpec

from . import resolvers, api, utils
from .enums import ParamType
from .errors import IncompatiblePathParameters
from .models import OperationSpecification, RequestOptions
from .parameters import Depends, Param, Params

PS = ParamSpec("PS")
RT = TypeVar("RT")


def get_operation(obj: Any, /) -> Optional["Operation"]:
    return getattr(obj, "operation", None)


def has_operation(obj: Any, /) -> bool:
    return get_operation(obj) is not None


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

        new_request_options: RequestOptions = self.build_request_options(arguments)
        request_options: RequestOptions = self.specification.request.merge(
            new_request_options
        )

        request: httpx.Request = request_options.build_request(self.client)

        return_annotation: Any = self.response_type

        if return_annotation is RequestOptions:
            return request_options
        if return_annotation is httpx.Request:
            return request

        client: Client = self.client if self.client is not None else Client()

        response: Response = client.send(request)

        if self.specification.response is not None:
            response_dependency: Depends = Depends(
                dependency=self.specification.response
            )

            return resolvers.resolve(
                response, response_dependency, request=self.specification.request
            )

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

            if isinstance(field, Params):
                if field.type is ParamType.QUERY:
                    query_params = query_params.merge(value)
                elif field.type is ParamType.HEADER:
                    headers.update(value)
                elif field.type is ParamType.COOKIE:
                    cookies.update(value)
                elif field.type is ParamType.PATH:
                    path_params.update(value)
                else:
                    raise Exception(f"Unknown multi-param: {field.type!r}")
            elif isinstance(field, Param):
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

        expected_path_params: Set[str] = utils.get_path_params(urllib.parse.unquote(str(self.specification.request.url)))
        actual_path_params: Set[str] = set(path_params)

        # Validate path params are correct
        if actual_path_params != expected_path_params:
            raise IncompatiblePathParameters(f"Incompatible path params. Got: {actual_path_params}, expected: {expected_path_params}")

        return RequestOptions(
            method=self.specification.request.method,
            url=urllib.parse.unquote(str(self.specification.request.url)).format(
                **path_params
            ),
            params=query_params,
            headers=headers,
            cookies=cookies,
            json=json,
        )

    def _is_method(self) -> bool:
        return bool(self.params and list(self.params)[0] == "self")

    def _get_arguments(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        bound_arguments: inspect.BoundArguments = inspect.signature(self.func).bind(
            *args, **kwargs
        )

        bound_arguments.apply_defaults()

        arguments: Dict[str, Any] = bound_arguments.arguments

        # TODO: Find a better fix for instance methods
        if arguments and list(arguments)[0] == "self":
            arguments.pop("self")

        argument_name: str
        argument: Any
        for argument_name, argument in arguments.items():
            if not isinstance(argument, Param):
                continue

            if not argument.has_default():
                raise ValueError(
                    f"{self.func.__name__}() missing argument: {argument_name!r}"
                )

            arguments[argument_name] = argument.get_default()

        return arguments

    @property
    def params(self) -> Dict[str, Param]:
        parameters: Dict[str, param.Parameter] = api.get_params(
            self.func, request=self.specification.request
        )

        return {parameter.name: parameter.spec for parameter in parameters.values()}

    @property
    def response_type(self) -> Any:
        return inspect.signature(self.func).return_annotation