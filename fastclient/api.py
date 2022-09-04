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
)

import httpx
import param
from param.sentinels import Missing
from pydantic import BaseModel

from . import utils
from .models import OperationSpecification, RequestOptions
from .parameters import (
    Body,
    Depends,
    Param,
    Path,
    Promise,
    Query,
)
from .parameter_functions import Headers, Cookies, QueryParams


def get_operations(cls: type, /) -> Dict[str, Callable]:
    return {
        member_name: member
        for member_name, member in inspect.getmembers(cls)
        if hasattr(member, "operation")
    }


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
