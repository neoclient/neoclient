import dataclasses
import inspect
import urllib.parse
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple

import httpx
import param
from param import Parameter
from param.utils import parse
from pydantic import BaseModel

from . import utils
from .errors import DuplicateParameter, IncompatiblePathParameters
from .models import RequestOptions
from .parameter_functions import Cookies, Headers, QueryParams
from .parameters import Body, Depends, Param, Params, Path, PathParams, Promise, Query


def _extract_path_params(parameters: Iterable[param.Parameter]) -> Set[str]:
    return {
        (
            parameter.default.alias
            if parameter.default.alias is not None
            else parameter.default.generate_alias(parameter.name)
        )
        for parameter in parameters
        if isinstance(parameter.default, Path)
    }


# DEPRECATED: DO NOT USE
def _infer_parameter(parameter: inspect.Parameter, /, *, path_params: Set[str] = set()):
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
            default=parse(parameter.default),
        )
    elif (
        parameter_type is not parameter.empty
        and isinstance(parameter_type, type)
        and any(issubclass(parameter_type, body_type) for body_type in body_types)
    ):
        return Body(
            alias=parameter.name,
            default=parse(parameter.default),
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
            default=parse(parameter.default),
        )


# NOT USED
def get_params(
    func: Callable, /, *, request: Optional[RequestOptions] = None
) -> Dict[str, param.Parameter]:
    path_params: Set[str] = (
        utils.get_path_params(urllib.parse.unquote(str(request.url)))
        if request is not None
        else set()
    )

    _inspect_params: List[inspect.Parameter] = list(
        inspect.signature(func).parameters.values()
    )

    raw_parameters = _inspect_params

    parameters: Dict[str, param.Parameter] = {}
    parameters_to_infer: List[inspect.Parameter] = []

    parameter: inspect.Parameter

    for parameter in raw_parameters:
        # NOTE: `Depends` doesn't subclass `Param`. This needs to be fixed.
        # "responses" (e.g. `responses.status_code`) also don't subclass `Param`...
        if isinstance(parameter.default, (Param, Body, Params, Depends, Promise)):
            parameters[parameter.name] = Parameter.from_parameter(parameter)
        else:
            parameters_to_infer.append(parameter)

    for parameter in parameters_to_infer:
        param_spec: Any = _infer_parameter(parameter, path_params=path_params)

        parameters[parameter.name] = dataclasses.replace(
            Parameter.from_parameter(parameter), default=param_spec
        )

    # NOTE: Validation currently disabled as the checks should differ depending on whether it's checking
    # an operation or a dependency
    # validate_params(parameters, request=request)

    return parameters


# NOT USED
def validate_params(
    params: Dict[str, param.Parameter], *, request: Optional[RequestOptions] = None
) -> None:
    expected_path_params: Set[str] = (
        utils.get_path_params(urllib.parse.unquote(str(request.url)))
        if request is not None
        else set()
    )

    actual_path_params: Set[str] = _extract_path_params(params.values())

    # Validate that only expected path params provided
    # In the event a `PathParams` parameter is being used, will have to defer this check for invokation.
    if expected_path_params != actual_path_params and not any(
        isinstance(parameter.default, PathParams) for parameter in params.values()
    ):
        raise IncompatiblePathParameters(
            f"Incompatible path params. Got: {actual_path_params}, expected: {expected_path_params}"
        )

    # Validate no duplicate parameters provided
    parameter_outer: param.Parameter
    for parameter_outer in params.values():
        if (
            not isinstance(parameter_outer.default, Param)
            or parameter_outer.default.alias is None
        ):
            continue

        parameter_inner: param.Parameter
        for parameter_inner in params.values():
            if parameter_inner is parameter_outer or not isinstance(
                parameter_inner.default, Param
            ):
                continue

            if (
                parameter_outer.default.type is parameter_inner.default.type
                and parameter_outer.default.alias == parameter_inner.default.alias
            ):
                raise DuplicateParameter(
                    f"Duplicate parameters: {parameter_outer!r} and {parameter_inner!r}"
                )
