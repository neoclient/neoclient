import dataclasses
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
from param import ParameterSpecification
import pydantic
from httpx import Request, Response
from param import ParameterType
from param.sentinels import Missing, MissingType
from pydantic import BaseModel
from typing_extensions import ParamSpec

from . import utils
from .enums import ParamType
from .models import OperationSpecification, RequestOptions
from .parameters import (
    Body,
    Depends,
    Param,
    Params,
    Path,
    Promise,
    Query,
    Header,
    Cookie,
)
from .parameter_functions import Headers, Cookies, QueryParams

T = TypeVar("T")

PT = ParamSpec("PT")
RT = TypeVar("RT")

### STABLE API ###


def resolve(
    response: Response,
    param: ParameterSpecification,
    /,
    *,
    target_type: Union[Any, MissingType] = Missing,
    request: Optional[RequestOptions] = None,
    cached_dependencies: Optional[Dict[Callable[..., Any], Any]] = None,
) -> Any:
    resolved: Any

    if cached_dependencies is None:
        cached_dependencies = {}

    if isinstance(param, Params):
        resolved = resolve_multi_param(
            response,
            param,
            annotation=target_type,
        )
    elif isinstance(param, Param):
        resolved = resolve_param(
            response,
            param,
            annotation=target_type,
            request=request,
        )
    elif isinstance(param, Depends):
        parameter_dependency_callable: Callable

        if param.dependency is not None:
            parameter_dependency_callable = param.dependency
        elif target_type not in (inspect._empty, Missing):
            if not callable(target_type):
                raise Exception("Dependency has non-callable annotation")

            parameter_dependency_callable = target_type
        else:
            raise Exception("Cannot depend on nothing!")

        parameter_dependency: Depends = Depends(
            parameter_dependency_callable, use_cache=param.use_cache
        )

        resolved = resolve_dependency(
            response,
            parameter_dependency,
            request=request,
            cached_dependencies=cached_dependencies,
        )

        # Cache resolved dependency
        cached_dependencies[parameter_dependency_callable] = resolved
    elif isinstance(param, Promise):
        resolved = resolve_promise(response, param, annotation=target_type)
    else:
        raise Exception(f"Unknown parameter spec class: {type(param)!r}")

    return resolved


### UNSTABLE API ###


def get_operations(cls: type, /) -> Dict[str, Callable]:
    return {
        member_name: member
        for member_name, member in inspect.getmembers(cls)
        if hasattr(member, "operation")
    }


def get_alias(parameter: param.Parameter, /) -> str:
    return (
        parameter.spec.alias
        if parameter.spec.alias is not None
        else parameter.spec.generate_alias(parameter.name)
    )


def _parse_obj(annotation: Union[MissingType, Any], obj: Any) -> Any:
    if type(obj) is annotation or annotation in (inspect._empty, Missing):
        return obj

    return pydantic.parse_obj_as(annotation, obj)


def resolve_query_param(
    response: Response,
    param: Query,
    /,
    *,
    annotation: Union[Any, MissingType] = Missing,
) -> Any:
    if param.alias is None:
        raise Exception("Cannot resolve a parameter without an alias")

    if param.alias in response.request.url.params:
        return _parse_obj(annotation, response.request.url.params[param.alias])
    else:
        return param.default


def resolve_header(
    response: Response,
    param: Header,
    /,
    *,
    annotation: Union[Any, MissingType] = Missing,
) -> Any:
    if param.alias is None:
        raise Exception("Cannot resolve a parameter without an alias")

    if param.alias in response.headers:
        return _parse_obj(annotation, response.headers[param.alias])
    else:
        return param.default


def resolve_cookie(
    response: Response,
    param: Cookie,
    /,
    *,
    annotation: Union[Any, MissingType] = Missing,
) -> Optional[str]:
    if param.alias is None:
        raise Exception("Cannot resolve a parameter without an alias")

    if param.alias in response.cookies:
        return _parse_obj(annotation, response.cookies[param.alias])
    else:
        return param.default


def resolve_body(
    response: Response, /, *, annotation: Union[Any, MissingType] = Missing
) -> Any:
    # TODO: Massively improve this implementation
    if annotation in (inspect._empty, Missing):
        return response.json()
    else:
        return pydantic.parse_raw_as(annotation, response.text)


def resolve_path_param(
    response: Response,
    param: Path,
    /,
    *,
    annotation: Union[Any, MissingType] = Missing,
    request: RequestOptions,
) -> str:
    if param.alias is None:
        raise Exception("Cannot resolve a parameter without an alias")

    path_params: Dict[str, Any] = utils.extract_path_params(
        urllib.parse.unquote(str(request.url)),
        urllib.parse.unquote(str(response.request.url)),
    )

    if param.alias in path_params:
        return _parse_obj(annotation, path_params[param.alias])
    else:
        return param.default


def resolve_promise(
    response: Response,
    promise: Promise,
    /,
    *,
    annotation: Union[Any, MissingType] = Missing,
) -> Union[Request, Response]:
    promised_type: Union[Type[Request], Type[Response]]

    if promise.promised_type is not None:
        promised_type = promise.promised_type
    elif annotation not in (inspect._empty, Missing):
        promised_type = annotation
    else:
        raise Exception("Cannot promise no type!")

    # TODO: Support more promised types?
    if promised_type is Response:
        return response
    elif promised_type is Request:
        return response.request
    else:
        raise Exception(f"Unsupported promised type: {promise.promised_type!r}")


def resolve_multi_param(
    response: Response,
    param: Params,
    /,
    *,
    annotation: Union[Any, MissingType] = Missing,
) -> Any:
    values: Dict[ParamType, Any] = {
        ParamType.QUERY: response.url.params,
        ParamType.HEADER: response.headers,
        ParamType.COOKIE: response.cookies,
    }

    return _parse_obj(annotation, values[param.type])


def resolve_param(
    response: Response,
    param: Param,
    /,
    *,
    annotation: Union[Any, MissingType] = Missing,
    request: Optional[RequestOptions] = None,
) -> Any:
    if param.type is ParamType.QUERY:
        return resolve_query_param(response, param, annotation=annotation)
    elif param.type is ParamType.HEADER:
        return resolve_header(response, param, annotation=annotation)
    elif param.type is ParamType.PATH:
        if request is None:
            raise Exception("Cannot resolve path param if no request provided")

        return resolve_path_param(
            response, param, annotation=annotation, request=request
        )
    elif param.type is ParamType.COOKIE:
        return resolve_cookie(response, param, annotation=annotation)
    elif param.type is ParamType.BODY:
        return resolve_body(response, annotation=annotation)
    else:
        raise Exception(f"Unknown ParamType: {param.type}")


def resolve_dependency(
    response: Response,
    dependency: Depends,
    /,
    *,
    request: Optional[RequestOptions] = None,
    cached_dependencies: Optional[Dict[Callable[..., Any], Any]] = None,
) -> Any:
    if dependency.dependency is None:
        raise Exception("Cannot resolve empty dependency")

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
        parameter_spec: ParameterSpecification = parameter.spec

        if isinstance(parameter_spec, Param) and not isinstance(parameter_spec, Params):
            parameter_alias: str = get_alias(parameter)

            parameter_spec = dataclasses.replace(parameter.spec, alias=parameter_alias)

        value: Any = resolve(
            response,
            parameter_spec,
            target_type=parameter.annotation,
            request=request,
            cached_dependencies=cached_dependencies,
        )

        if parameter.type in (
            ParameterType.POSITIONAL_ONLY,
            ParameterType.VAR_POSITIONAL,
        ):
            args.append(value)
        else:
            kwargs[parameter.name] = value

    return dependency.dependency(*args, **kwargs)


def _build_parameter(
    parameter: Parameter, spec: param.ParameterSpecification
) -> param.Parameter:
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


def _infer_parameter(parameter: Parameter, /, *, path_params: Set[str] = set()):
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

    # NOTE: Need to check later that there's no conflict with any explicityly provided parameters
    # E.g. (path_param: str, same_path_param: str = Param(alias="path_param"))
    if parameter.name in path_params:
        return Path(
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
        return Body(
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
        return Promise(parameter_type)
    elif (
        parameter_type is not parameter.empty
        and isinstance(parameter_type, type)
        and any(issubclass(parameter_type, httpx_type) for httpx_type in httpx_types)
    ):
        if parameter_type is httpx.Headers:
            return Headers()
        elif parameter_type is httpx.Cookies:
            return Cookies()
        elif parameter_type is httpx.QueryParams:
            return QueryParams()
        else:
            raise Exception(f"Unknown httpx dependency type: {parameter.annotation!r}")
    else:
        return Query(
            alias=parameter.name,
            default=(
                parameter.default
                if parameter.default is not parameter.empty
                else Missing
            ),
        )


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
        param_spec: Any = _infer_parameter(parameter, path_params=path_params)

        parameters[parameter.name] = _build_parameter(parameter, param_spec)

    actual_path_params: Set[str] = _extract_path_params(parameters.values())

    # Validate that only expected path params provided
    if path_params != actual_path_params:
        raise ValueError(
            f"Incompatible path params. Got: {actual_path_params}, expected: {path_params}"
        )

    return parameters


def build_operation_specification(
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
