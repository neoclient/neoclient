import functools
import inspect
import pydantic
from inspect import Parameter, Signature
from types import FunctionType
from typing import (
    Any,
    Callable,
    Dict,
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
from arguments import Arguments
from httpx import Response
from param import ParameterType
from param.sentinels import Missing, MissingType
from pydantic import BaseModel
from typing_extensions import ParamSpec

from . import utils, encoders
from .enums import Annotation, HttpMethod, ParamType
from .models import ClientConfig, Request, Specification
from .params import Body, Depends, Param, Params, Path, Query

T = TypeVar("T")

PT = ParamSpec("PT")
RT = TypeVar("RT")


def get_specification(obj: Any, /) -> Optional[Specification]:
    return annotate.get_annotations(obj).get(Annotation.SPECIFICATION)


def has_specification(obj: Any, /) -> bool:
    return Annotation.SPECIFICATION in annotate.get_annotations(obj)


def get_specifications(cls: type, /) -> Dict[str, Specification]:
    return {
        member_name: annotate.get_annotations(member)[Annotation.SPECIFICATION]
        for member_name, member in inspect.getmembers(cls)
        if isinstance(member, FunctionType)
        and Annotation.SPECIFICATION in annotate.get_annotations(member)
    }


def get_response_arguments(
    response: Response,
    parameters: Dict[str, param.Parameter],
    request: Request,
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
                value = dict(
                    response.headers
                )  # TODO: Respect httpx use of `Headers` object that allows multiple entries of same key
            elif parameter.spec.type is ParamType.COOKIE:
                value = dict(
                    response.cookies
                )  # TODO: Respect httpx use of `Cookies` object that contains more cookie metadata
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
    _client_config: ClientConfig
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

        self._client_config = ClientConfig(
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
        specifications: Dict[str, Specification] = get_specifications(protocol)

        attributes: dict = {"__module__": protocol.__module__}

        func_name: str
        specification: Specification
        for func_name, specification in specifications.items():
            func: FunctionType = getattr(protocol, func_name)

            attributes[func_name] = self._method(specification, func)

        return type(protocol.__name__, (BaseService,), attributes)()

    def _method(
        self, specification: Specification, func: Callable[PT, RT], /
    ) -> Callable[PT, RT]:
        signature: Signature = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args: PT.args, **kwargs: PT.kwargs) -> Union[Any, NoReturn]:
            arguments: Dict[str, Any] = Arguments(*args, **kwargs).bind(func).asdict()

            argument_name: str
            argument: Any
            for argument_name, argument in arguments.items():
                if not isinstance(argument, Param):
                    continue

                if not argument.has_default():
                    raise ValueError(
                        f"{func.__name__}() missing argument: {argument_name!r}"
                    )

                arguments[argument_name] = argument.default

            destinations: Dict[ParamType, Dict[str, Any]] = {}

            parameter: str
            field: Param
            for parameter, field in specification.params.items():
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

            method: str = specification.request.method
            url: str = specification.request.url.format(
                **destinations.get(ParamType.PATH, {})
            )
            params: dict = {
                **specification.request.params,
                **destinations.get(ParamType.QUERY, {}),
            }
            headers: dict = {
                **specification.request.headers,
                **destinations.get(ParamType.HEADER, {}),
            }
            cookies: dict = {
                **specification.request.cookies,
                **destinations.get(ParamType.COOKIE, {}),
            }

            request: Request = Request(
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

            return_annotation: Any = signature.return_annotation

            if return_annotation is Request:
                return request
            if return_annotation is httpx.Request:
                return httpx_request

            response: Response = self.client.send(httpx_request)

            if specification.response is not None:
                response_params: Dict[str, param.Parameter] = get_params(
                    specification.response, request=specification.request
                )
                response_arguments: Arguments = get_response_arguments(
                    response, response_params, specification.request
                )

                return response_arguments.call(specification.response)

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

        return wrapper

    def request(
        self,
        method: str,
        endpoint: Optional[str] = None,
        /,
        *,
        response: Optional[Callable[..., Any]] = None,
    ):
        def decorator(func: Callable[PT, RT], /) -> Callable[PT, RT]:
            uri: str = (
                endpoint if endpoint is not None else Path.generate_alias(func.__name__)
            )

            specification: Specification = build_request_specification(
                func,
                method,
                uri,
                response=response,
            )

            return self._method(specification, func)

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
    func: Callable, /, *, request: Optional[Request] = None
) -> Dict[str, param.Parameter]:
    path_params: Set[str] = (
        utils.get_path_params(request.url) if request is not None else set()
    )

    _inspect_params: List[Parameter] = list(inspect.signature(func).parameters.values())

    # Dealing with a request
    if has_specification(func):
        raw_parameters = _inspect_params[1:]  # ignore first arg (self)
    # Dealing with a non-request, likely a converter
    else:
        raw_parameters = _inspect_params

    parameters: Dict[str, param.Parameter] = {}
    parameters_to_infer: List[Parameter] = []

    parameter: Parameter

    for parameter in raw_parameters:
        # NOTE: `Depends` doesn't subclass `Param`. This needs to be fixed.
        if isinstance(parameter.default, (Param, Depends)):
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
    request: Request = Request(
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
