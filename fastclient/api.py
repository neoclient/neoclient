from dataclasses import dataclass
import functools
import inspect
from inspect import Parameter, Signature
from types import FunctionType
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    List,
    NoReturn,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

import annotate
import httpx
import param
import parse
import pydantic
from arguments import Arguments
from httpx import Response
from param import ParameterType
from param.sentinels import Missing, MissingType
from pydantic import BaseModel
from typing_extensions import ParamSpec

from . import annotators, encoders, utils
from .enums import Annotation, HttpMethod, ParamType
from .models import ClientOptions, RequestOptions, Specification
from .params import Body, Depends, Param, Params, Path, Promise, Query
from .errors import UnboundOperationException

T = TypeVar("T")

PT = ParamSpec("PT")
RT = TypeVar("RT")


def get_specification(obj: Any, /) -> Optional[Specification]:
    return annotate.get_annotations(obj).get(Annotation.SPECIFICATION)


def has_specification(obj: Any, /) -> bool:
    return Annotation.SPECIFICATION in annotate.get_annotations(obj)


def get_operations(cls: type, /) -> List["Operation"]:
    return [
        member
        for _, member in inspect.getmembers(cls)
        if isinstance(member, Operation)
    ]


def get_response_arguments(
    response: Response,
    parameters: Dict[str, param.Parameter],
    request: RequestOptions,
    /,
    *,
    cached_dependencies: Optional[Dict[Callable[..., Any], Any]] = None,
) -> Arguments:
    args: List[Any] = []
    kwargs: Dict[str, Any] = {}

    if cached_dependencies is None:
        cached_dependencies = {}

    parameter: param.Parameter
    for parameter in parameters.values():
        value: Any = None

        if isinstance(parameter.spec, Params):
            if parameter.spec.type is ParamType.QUERY:
                value = dict(response.request.url.params)
            elif parameter.spec.type is ParamType.HEADER:
                if parameter.annotation in (inspect._empty, Missing, httpx.Headers):
                    value = response.headers
                elif parameter.annotation is dict:
                    value = dict(response.headers)
                else:
                    raise Exception(f"Headers dependency has incompatible annotation: {parameter.annotation!r}")
            elif parameter.spec.type is ParamType.COOKIE:
                if parameter.annotation in (inspect._empty, Missing, httpx.Cookies):
                    value = response.cookies
                elif parameter.annotation is dict:
                    value = dict(response.cookies)
                else:
                    raise Exception(f"Cookies dependency has incompatible annotation: {parameter.annotation!r}")
            else:
                raise Exception(f"Unknown multi-param of type {parameter.spec.type}")
        elif isinstance(parameter.spec, Param):
            parameter_alias: str = (
                parameter.spec.alias
                if parameter.spec.alias is not None
                else parameter.spec.generate_alias(parameter.name)
            )

            if parameter.spec.type is ParamType.QUERY:
                value = response.request.url.params[parameter_alias]
            elif parameter.spec.type is ParamType.HEADER:
                value = response.headers[parameter_alias]
            elif parameter.spec.type is ParamType.PATH:
                parse_result: Optional[parse.Result] = parse.parse(
                    request.url, response.request.url.path
                )

                if parse_result is None:
                    raise Exception(
                        f"Failed to parse uri {response.request.url.path!r} against format spec {request.url!r}"
                    )

                value = parse_result.named[parameter_alias]
            elif parameter.spec.type is ParamType.COOKIE:
                value = response.cookies[parameter_alias]
            elif parameter.spec.type is ParamType.BODY:
                if parameter.annotation is not inspect._empty:
                    value = pydantic.parse_raw_as(parameter.annotation, response.text)
                else:
                    value = response.json()
            else:
                raise Exception(f"Unknown ParamType: {parameter.spec.type}")
        elif isinstance(parameter.spec, Depends):
            if (
                cached_dependencies is not None
                and parameter.spec.use_cache
                and parameter.spec.dependency in cached_dependencies
            ):
                value = cached_dependencies[parameter.spec.dependency]
            else:
                if parameter.spec.dependency is None:
                    raise Exception(
                        "TODO: Support dependencies with no explicit dependency"
                    )
                else:
                    sub_parameters: Dict[str, param.Parameter] = get_params(
                        parameter.spec.dependency, request=request
                    )
                    sub_arguments: Arguments = get_response_arguments(
                        response,
                        sub_parameters,
                        request,
                        cached_dependencies=cached_dependencies,
                    )

                    value = sub_arguments.call(parameter.spec.dependency)

                cached_dependencies[parameter.spec.dependency] = value
        elif isinstance(parameter.spec, Promise):
            promised_type: type

            if parameter.spec.promised_type is not None:
                promised_type = parameter.spec.promised_type
            elif parameter.annotation is not inspect._empty:
                promised_type = parameter.annotation
            else:
                raise Exception("Cannot promise no type!")

            # TODO: Support more promised types
            if promised_type is httpx.Response:
                value = response
            elif promised_type is httpx.Request:
                value = request
            else:
                raise Exception(
                    f"Unsupported promised type: {parameter.spec.promised_type!r}"
                )
        else:
            raise Exception(f"Unknown parameter spec class: {type(parameter.spec)}")

        if parameter.type in (
            ParameterType.POSITIONAL_ONLY,
            ParameterType.VAR_POSITIONAL,
        ):
            args.append(value)
        else:
            kwargs[parameter.name] = value

    return Arguments(*args, **kwargs)


class BaseService:
    def __repr__(self) -> str:
        return f"<{type(self).__name__}()>"


class FastClient:
    _client_config: ClientOptions
    _client: Optional[httpx.Client]

    def __init__(
        self,
        base_url: Union[httpx.URL, str] = "",
        *,
        client: Union[None, httpx.Client, MissingType] = Missing,
        headers: Union[
            httpx.Headers,
            Dict[str, str],
            Dict[bytes, bytes],
            Sequence[Tuple[str, str]],
            Sequence[Tuple[bytes, bytes]],
            None,
        ] = None,
    ) -> None:
        # TODO: Add other named params and use proper types beyond just `headers`

        self._client_config = ClientOptions(
            base_url=base_url,
            headers=headers,
        )

        if client is Missing:
            self._client = self._client_config.build()
        elif client is None:
            if not self._client_config.is_default():
                raise Exception(
                    "Cannot specify both `client` and other config options."
                )

            self._client = None
        else:
            self._client = client

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            return self._client_config.build()

        return self._client

    def __repr__(self) -> str:
        return f"{type(self).__name__}(client={self.client!r})"

    def create(self, protocol: Type[T], /) -> T:
        operations: List["Operation"] = get_operations(protocol)

        attributes: dict = {"__module__": protocol.__module__}

        operation: "Operation"
        for operation in operations:
            bound_operation: BoundOperation = operation.bind(self)

            attributes[operation.func.__name__] = functools.wraps(operation.func)(bound_operation)

        return type(protocol.__name__, (BaseService,), attributes)()

    def request(
        self,
        method: str,
        endpoint: Optional[str] = None,
        /,
        *,
        response: Optional[Callable[..., Any]] = None,
    ):
        def decorator(func: Callable[PT, RT], /) -> BoundOperation[PT, RT]:
            uri: str = (
                endpoint if endpoint is not None else Path.generate_alias(func.__name__)
            )

            return annotators.request(method, uri, response=response)(
                func
            ).bind(self)

        return decorator

    def put(self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None):
        return self.request(HttpMethod.PUT.name, endpoint, response=response)

    def get(self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None):
        return self.request(HttpMethod.GET.name, endpoint, response=response)

    def post(self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None):
        return self.request(HttpMethod.POST.name, endpoint, response=response)

    def head(self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None):
        return self.request(HttpMethod.HEAD.name, endpoint, response=response)

    def patch(self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None):
        return self.request(HttpMethod.PATCH.name, endpoint, response=response)

    def delete(
        self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
    ):
        return self.request(HttpMethod.DELETE.name, endpoint, response=response)

    def options(
        self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
    ):
        return self.request(HttpMethod.OPTIONS.name, endpoint, response=response)


def _build_parameter(parameter: Parameter, spec: Param) -> param.Parameter:
    return param.Parameter(
        name=parameter.name,
        annotation=parameter.annotation,
        type=getattr(param.ParameterType, parameter.kind.name),
        spec=spec,
    )


def _extract_path_params(parameters: Iterable[param.Parameter]) -> Set[str]:
    return {
        (
            parameter.spec.alias
            if parameter.spec.alias is not None
            else parameter.spec.generate_alias(parameter.name)
        )
        for parameter in parameters
        if isinstance(parameter.spec, Path)
    }


def get_params(
    func: Callable, /, *, request: Optional[RequestOptions] = None
) -> Dict[str, param.Parameter]:
    path_params: Set[str] = (
        utils.get_path_params(str(request.url)) if request is not None else set()
    )

    _inspect_params: List[Parameter] = list(inspect.signature(func).parameters.values())

    raw_parameters = _inspect_params

    parameters: Dict[str, param.Parameter] = {}
    parameters_to_infer: List[Parameter] = []

    parameter: Parameter

    for parameter in raw_parameters:
        # NOTE: `Depends` doesn't subclass `Param`. This needs to be fixed.
        # "responses" (e.g. `responses.status_code`) also don't subclass `Param`...
        if isinstance(parameter.default, (Param, Depends, Promise)):
            parameters[parameter.name] = _build_parameter(parameter, parameter.default)
        else:
            parameters_to_infer.append(parameter)

    for parameter in parameters_to_infer:
        param_cls: Type[Param] = Query

        parameter_type: type = parameter.annotation

        body_types: Tuple[type, ...] = (BaseModel, dict)

        if parameter.name in path_params and not any(
            isinstance(field, Path) and field.alias in path_params
            for field in parameters.values()
        ):
            param_cls = Path
        elif (
            parameter.annotation is not parameter.empty
            and isinstance(parameter_type, type)
            and any(issubclass(parameter_type, body_type) for body_type in body_types)
        ):
            param_cls = Body

        param_spec: Param = param_cls(
            alias=parameter.name,
            default=parameter.default
            if parameter.default is not parameter.empty
            else Missing,
        )

        parameters[parameter.name] = _build_parameter(parameter, param_spec)

    actual_path_params: Set[str] = _extract_path_params(parameters.values())

    # Validate that only expected path params provided
    if path_params != actual_path_params:
        raise ValueError(
            f"Incompatible path params. Got: {actual_path_params}, expected: {path_params}"
        )

    return parameters


def build_request_specification(
    func: Callable,
    method: str,
    endpoint: str,
    *,
    response: Optional[Callable[..., Any]] = None,
) -> Specification:
    request: RequestOptions = RequestOptions(
        method=method,
        url=endpoint,
    )

    parameters: Dict[str, param.Parameter] = get_params(func, request=request)

    param_specs: Dict[str, Param] = {
        parameter.name: parameter.spec for parameter in parameters.values()
    }

    return Specification(
        request=request,
        response=response,
        params=param_specs,
    )

@dataclass
class Operation(Generic[PT, RT]):
    func: Callable[PT, RT]

    def __call__(self, *args: PT.args, **kwargs: PT.kwargs) -> RT:
        raise UnboundOperationException("Operation is unbound")

    @property
    def specification(self) -> Specification:
        return annotate.get_annotations(self.func)[Annotation.SPECIFICATION]

    def bind(self, client: FastClient, /) -> "BoundOperation":
        bound_operation: BoundOperation = BoundOperation(self.func, client=client)

        return functools.wraps(self.func)(bound_operation)


@dataclass
class BoundOperation(Operation[PT, RT]):
    client: FastClient

    def __call__(self, *args: PT.args, **kwargs: PT.kwargs) -> Any:
        signature: Signature = inspect.signature(self.func)

        arguments: Dict[str, Any]

        # TODO: Find a better fix for instance methods!
        if self.specification.params and list(self.specification.params)[0] == "self":
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
            json = encoders.jsonable_encoder(list(body_params.values())[0])
        # If there are multiple body params, construct a multi-level dict
        # of each body parameter. E.g. (user: User, item: Item) -> {"user": ..., "item": ...}
        elif body_params:
            json = {
                key: encoders.jsonable_encoder(val)
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

        httpx_request: httpx.Request = self.client.client.build_request(
            method=method,
            url=url,
            params=params,
            headers=headers,
            cookies=cookies,
            json=json,
        )

        return_annotation: Any = signature.return_annotation

        if return_annotation is RequestOptions:
            return request
        if return_annotation is httpx.Request:
            return httpx_request

        response: Response = self.client.client.send(httpx_request)

        if self.specification.response is not None:
            response_params: Dict[str, param.Parameter] = get_params(
                self.specification.response, request=self.specification.request
            )
            response_arguments: Arguments = get_response_arguments(
                response, response_params, self.specification.request
            )

            return response_arguments.call(self.specification.response)

        if return_annotation is signature.empty:
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
