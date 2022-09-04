import inspect
import urllib.parse
from inspect import Parameter
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

import httpx
import param
import parse
import pydantic
from arguments import Arguments
from httpx import Request, Response
from param import ParameterType
from param.sentinels import Missing
from pydantic import BaseModel
from typing_extensions import ParamSpec

from . import utils
from .enums import ParamType
from .models import OperationSpecification, RequestOptions
from .parameters import Body, Depends, Param, Params, Path, Promise, Query
from .parameter_functions import Headers, Cookies, QueryParams

T = TypeVar("T")

PT = ParamSpec("PT")
RT = TypeVar("RT")


def get_operations(cls: type, /) -> Dict[str, Callable]:
    return {
        member_name: member
        for member_name, member in inspect.getmembers(cls)
        if hasattr(member, "operation")
    }


def resolve_query_params(
    response: Response, parameter: param.Parameter, /
) -> Union[httpx.QueryParams, Dict[str, str]]:
    if parameter.annotation in (inspect._empty, Missing, httpx.QueryParams):
        return response.url.params
    elif parameter.annotation is dict:
        return dict(response.url.params)
    else:
        raise Exception(
            f"{parameter!r} has incompatible annotation: {parameter.annotation!r}"
        )


def resolve_headers(
    response: Response, parameter: param.Parameter, /
) -> Union[httpx.Headers, Dict[str, str]]:
    if parameter.annotation in (inspect._empty, Missing, httpx.Headers):
        return response.headers
    elif parameter.annotation is dict:
        return dict(response.headers)
    else:
        raise Exception(
            f"{parameter!r} has incompatible annotation: {parameter.annotation!r}"
        )


def resolve_cookies(
    response: Response, parameter: param.Parameter, /
) -> Union[httpx.Cookies, Dict[str, str]]:
    if parameter.annotation in (inspect._empty, Missing, httpx.Cookies):
        return response.cookies
    elif parameter.annotation is dict:
        return dict(response.cookies)
    else:
        raise Exception(
            f"{parameter!r} has incompatible annotation: {parameter.annotation!r}"
        )


def resolve_query_param(response: Response, parameter: param.Parameter, /) -> str:
    parameter_alias: str = (
        parameter.spec.alias
        if parameter.spec.alias is not None
        else parameter.spec.generate_alias(parameter.name)
    )

    return response.request.url.params[parameter_alias]


def resolve_header(response: Response, parameter: param.Parameter, /) -> str:
    parameter_alias: str = (
        parameter.spec.alias
        if parameter.spec.alias is not None
        else parameter.spec.generate_alias(parameter.name)
    )

    return response.headers[parameter_alias]


def resolve_path_param(
    response: Response, parameter: param.Parameter, request: RequestOptions, /
) -> str:
    parameter_alias: str = (
        parameter.spec.alias
        if parameter.spec.alias is not None
        else parameter.spec.generate_alias(parameter.name)
    )

    parse_result: Optional[parse.Result] = parse.parse(
        request.url, response.request.url.path
    )

    if parse_result is None:
        raise Exception(
            f"Failed to parse uri {response.request.url.path!r} against format spec {request.url!r}"
        )

    return parse_result.named[parameter_alias]


def resolve_cookie(response: Response, parameter: param.Parameter, /) -> str:
    parameter_alias: str = (
        parameter.spec.alias
        if parameter.spec.alias is not None
        else parameter.spec.generate_alias(parameter.name)
    )

    return response.cookies[parameter_alias]


def resolve_body(response: Response, parameter: param.Parameter, /) -> Any:
    if parameter.annotation is not inspect._empty:
        return pydantic.parse_raw_as(parameter.annotation, response.text)
    else:
        return response.json()


def resolve_promise(
    response: Response, parameter: param.Parameter, /
) -> Union[Request, Response]:
    promised_type: Union[Type[Request], Type[Response]]

    if parameter.spec.promised_type is not None:
        promised_type = parameter.spec.promised_type
    elif parameter.annotation not in (inspect._empty, Missing):
        promised_type = parameter.annotation
    else:
        raise Exception("Cannot promise no type!")

    # TODO: Support more promised types?
    if promised_type is Response:
        return response
    elif promised_type is Request:
        return response.request
    else:
        raise Exception(f"Unsupported promised type: {parameter.spec.promised_type!r}")


def resolve_params(response: Response, parameter: param.Parameter, /) -> Any:
    if parameter.spec.type is ParamType.QUERY:
        return resolve_query_params(response, parameter)
    elif parameter.spec.type is ParamType.HEADER:
        return resolve_headers(response, parameter)
    elif parameter.spec.type is ParamType.COOKIE:
        return resolve_cookies(response, parameter)
    else:
        raise Exception(f"Unknown multi-param of type {parameter.spec.type}")


def resolve_param(
    response: Response,
    parameter: param.Parameter,
    /,
    *,
    request: Optional[RequestOptions] = None,
) -> Any:
    if parameter.spec.type is ParamType.QUERY:
        return resolve_query_param(response, parameter)
    elif parameter.spec.type is ParamType.HEADER:
        return resolve_header(response, parameter)
    elif parameter.spec.type is ParamType.PATH:
        return resolve_path_param(response, parameter, request)
    elif parameter.spec.type is ParamType.COOKIE:
        return resolve_cookie(response, parameter)
    elif parameter.spec.type is ParamType.BODY:
        return resolve_body(response, parameter)
    else:
        raise Exception(f"Unknown ParamType: {parameter.spec.type}")


def resolve_dependency(
    response: Response,
    dependency: Depends,
    /,
    *,
    request: Optional[RequestOptions] = None,
    cached_dependencies: Optional[Dict[Callable[..., Any], Any]] = None,
) -> Any:
    if dependency.dependency is None:
        raise Exception("TODO: Support dependencies with no explicit dependency")

    if (
        cached_dependencies is not None
        and dependency.use_cache
        and dependency.dependency in cached_dependencies
    ):
        return cached_dependencies[dependency.dependency]

    parameters: Dict[str, param.Parameter] = get_params(
        dependency.dependency, request=request
    )

    args: List[Any] = []
    kwargs: Dict[str, Any] = {}

    if cached_dependencies is None:
        cached_dependencies = {}

    parameter: param.Parameter
    for parameter in parameters.values():
        value: Any = None

        if isinstance(parameter.spec, Params):
            value = resolve_params(response, parameter)
        elif isinstance(parameter.spec, Param):
            value = resolve_param(response, parameter, request=request)
        elif isinstance(parameter.spec, Depends):
            value = resolve_dependency(
                response,
                parameter.spec,
                request=request,
                cached_dependencies=cached_dependencies,
            )

            # Cache resolved dependency
            cached_dependencies[parameter.spec.dependency] = value
        elif isinstance(parameter.spec, Promise):
            value = resolve_promise(response, parameter)
        else:
            raise Exception(f"Unknown parameter spec class: {type(parameter.spec)}")

        if parameter.type in (
            ParameterType.POSITIONAL_ONLY,
            ParameterType.VAR_POSITIONAL,
        ):
            args.append(value)
        else:
            kwargs[parameter.name] = value

    arguments: Arguments = Arguments(*args, **kwargs)

    return arguments.call(dependency.dependency)


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
        utils.get_path_params(urllib.parse.unquote(str(request.url)))
        if request is not None
        else set()
    )

    _inspect_params: List[Parameter] = list(inspect.signature(func).parameters.values())

    # TODO: Find a better fix for methods!
    if _inspect_params and _inspect_params[0].name == "self":
        raw_parameters = _inspect_params[1:]
    else:
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
        param_spec: Any

        parameter_type: type = parameter.annotation

        body_types: Tuple[type, ...] = (BaseModel, dict)
        httpx_types: Tuple[type, ...] = (
            httpx.Headers,
            httpx.Cookies,
            httpx.QueryParams,
        )
        promise_types: Tuple[type, ...] = (
            httpx.Request,
            httpx.Response,
        )

        if parameter.name in path_params and not any(
            isinstance(field, Path) and field.alias in path_params
            for field in parameters.values()
        ):
            param_spec = Path(
                alias=parameter.name,
                default=(
                    parameter.default
                    if parameter.default is not parameter.empty
                    else Missing
                ),
            )
        elif (
            parameter_type is not parameter.empty
            and isinstance(parameter_type, type)
            and any(issubclass(parameter_type, body_type) for body_type in body_types)
        ):
            param_spec = Body(
                alias=parameter.name,
                default=(
                    parameter.default
                    if parameter.default is not parameter.empty
                    else Missing
                ),
            )
        elif (
            parameter_type is not parameter.empty
            and isinstance(parameter_type, type)
            and any(
                issubclass(parameter_type, promise_type) for promise_type in promise_types
            )
        ):
            param_spec = Promise(parameter_type)
        elif (
            parameter_type is not parameter.empty
            and isinstance(parameter_type, type)
            and any(
                issubclass(parameter_type, httpx_type) for httpx_type in httpx_types
            )
        ):
            if parameter_type is httpx.Headers:
                param_spec = Headers()
            elif parameter_type is httpx.Cookies:
                param_spec = Cookies()
            elif parameter_type is httpx.QueryParams:
                param_spec = QueryParams()
            else:
                raise Exception(
                    f"Unknown httpx dependency type: {parameter.annotation!r}"
                )
        else:
            param_spec = Query(
                alias=parameter.name,
                default=(
                    parameter.default
                    if parameter.default is not parameter.empty
                    else Missing
                ),
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
) -> OperationSpecification:
    request: RequestOptions = RequestOptions(
        method=method,
        url=endpoint,
    )

    # Assert params are valid
    get_params(func, request=request)

    return OperationSpecification(
        request=request,
        response=response,
    )
