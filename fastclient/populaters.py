import dataclasses
import inspect
import urllib.parse
from typing import Any, Callable, Dict, Mapping, Optional, Protocol, Set, Union

import fastapi.encoders
import httpx
import param
import param.models
from param.sentinels import Missing, MissingType
import pydantic

from . import api, utils
from .enums import ParamType
from .errors import IncompatiblePathParameters, InvalidParameterSpecification
from .models import RequestOptions
from .parameters import (
    Body,
    Param,
    Params,
    Header,
    Headers,
    Path,
    QueryParams,
    Query,
    Cookie,
    Cookies,
    PathParams,
)
from .types import HeaderTypes, QueryParamTypes, CookieTypes


class Composer(Protocol):
    def __call__(
        self, request: RequestOptions, parameter: param.Parameter, value: Any
    ) -> None:
        ...


def _parse_obj(annotation: Union[MissingType, Any], obj: Any) -> Any:
    if type(obj) is annotation or annotation in (inspect._empty, Missing):
        return obj

    return pydantic.parse_obj_as(annotation, obj)


def feed_request_query_param(request: RequestOptions, param: Query, value: str) -> None:
    if param.alias is None:
        raise Exception(f"Cannot feed param {param!r} if it has no alias")

    resolved_value: str = value if value is not Missing else param.get_default()

    request.add_query_param(param.alias, resolved_value)


def feed_request_header(request: RequestOptions, param: Header, value: str) -> None:
    if param.alias is None:
        raise Exception(f"Cannot feed param {param!r} if it has no alias")

    resolved_value: str = value if value is not Missing else param.get_default()

    request.add_header(param.alias, resolved_value)


def feed_request_cookie(request: RequestOptions, param: Cookie, value: str) -> None:
    if param.alias is None:
        raise Exception(f"Cannot feed param {param!r} if it has no alias")

    resolved_value: str = value if value is not Missing else param.get_default()

    request.add_cookie(param.alias, resolved_value)


def feed_request_path_param(request: RequestOptions, param: Path, value: str) -> None:
    if param.alias is None:
        raise Exception(f"Cannot feed param {param!r} if it has no alias")

    resolved_value: str = value if value is not Missing else param.get_default()

    request.add_path_param(param.alias, resolved_value)


def feed_request_body(request: RequestOptions, param: Body, value: Any) -> None:
    resolved_value: Any = fastapi.encoders.jsonable_encoder(
        value if value is not None else param.get_default()
    )

    if param.embed:
        if param.alias is None:
            raise Exception(f"Cannot embed body param {param!r} if it has no alias")

        resolved_value = {param.alias: resolved_value}

    # If there's only one body param, or this param shouln't be embedded in any pre-existing json,
    # make it the entire JSON request body
    if request.json is None or not param.embed:
        request.json = resolved_value
    else:
        request.json.update(resolved_value)


def feed_request_query_params(
    request: RequestOptions,
    param: QueryParams,
    value: QueryParamTypes,
) -> None:
    resolved_value: httpx.QueryParams = (
        httpx.QueryParams(value) if value is not Missing else param.get_default()
    )

    request.add_query_params(resolved_value)


def feed_request_headers(
    request: RequestOptions,
    param: Headers,
    value: HeaderTypes,
) -> None:
    resolved_value: httpx.Headers = (
        httpx.Headers(value) if value is not Missing else param.get_default()
    )

    request.add_headers(resolved_value)


def feed_request_cookies(
    request: RequestOptions,
    param: Cookies,
    value: CookieTypes,
) -> None:
    resolved_value: httpx.Cookies = (
        httpx.Cookies(value) if value is not Missing else param.get_default()
    )

    request.add_cookies(resolved_value)


def feed_request_path_params(
    request: RequestOptions,
    param: Cookies,
    value: Dict[str, Any],
) -> None:
    resolved_value: Dict[str, Any] = (
        value if value is not Missing else param.get_default()
    )

    request.add_path_params(resolved_value)


def feed_request_param(
    request: RequestOptions, parameter: param.Parameter, value: Any
) -> None:
    spec: Param

    if not isinstance(parameter.spec, Param):
        raise Exception("Parameter is not a Param")
    else:
        spec = parameter.spec

    field_name: str = (
        spec.alias if spec.alias is not None else spec.generate_alias(parameter.name)
    )

    # Ensure the parameter has an alias
    spec = dataclasses.replace(spec, alias=field_name)

    # The field is not required, it can be omitted
    if value is None and not spec.required:
        return

    if spec.type is ParamType.QUERY:
        # Convert the value
        value = _parse_obj(str, value)

        feed_request_query_param(request, spec, value)
    elif spec.type is ParamType.HEADER:
        # Convert the value
        value = _parse_obj(str, value)

        feed_request_header(request, spec, value)
    elif spec.type is ParamType.COOKIE:
        # Convert the value
        value = _parse_obj(str, value)

        feed_request_cookie(request, spec, value)
    elif spec.type is ParamType.PATH:
        # Convert the value
        value = _parse_obj(str, value)

        feed_request_path_param(request, spec, value)
    elif spec.type is ParamType.BODY:
        feed_request_body(request, spec, value)
    else:
        raise Exception(f"Unknown ParamType: {spec.type!r}")


def feed_request_params(
    request: RequestOptions, parameter: param.Parameter, value: Any
) -> None:
    spec: Params

    if not isinstance(parameter.spec, Params):
        raise Exception("Parameter is not a Params")
    else:
        spec = parameter.spec

    if spec.type is ParamType.QUERY:
        feed_request_query_params(request, spec, value)
    elif spec.type is ParamType.HEADER:
        feed_request_headers(request, spec, value)
    elif spec.type is ParamType.COOKIE:
        feed_request_cookies(request, spec, value)
    elif spec.type is ParamType.PATH:
        feed_request_path_params(request, spec, value)
    else:
        raise Exception(f"Unknown multi-param: {spec.type!r}")


whitelisted_operation_params: Dict[type, Composer] = {
    Query: feed_request_param,
    Header: feed_request_param,
    Cookie: feed_request_param,
    Path: feed_request_param,
    Body: feed_request_param,
    QueryParams: feed_request_params,
    Headers: feed_request_params,
    Cookies: feed_request_params,
    PathParams: feed_request_params,
}


def compose(request: RequestOptions, parameter: param.Parameter, value: Any) -> Any:
    spec_type: type
    feeder_function: Composer
    for spec_type, feeder_function in whitelisted_operation_params.items():
        if isinstance(parameter.spec, spec_type):
            feeder_function(request, parameter, value)

            break
    else:
        raise InvalidParameterSpecification(
            f"Invalid operation parameter specification: {parameter.spec!r}"
        )


def _validate_request_options(request: RequestOptions, /) -> None:
    missing_path_params: Set[str] = utils.get_path_params(
        urllib.parse.unquote(str(request.url))
    )

    # Validate path params are correct
    if missing_path_params:
        raise IncompatiblePathParameters(
            f"Incompatible path params. Missing: {missing_path_params}"
        )

def get_operation_params(
    func: Callable, /, *, request: Optional[RequestOptions] = None
) -> Dict[str, param.Parameter]:
    params: Dict[str, param.Parameter] = api.get_params(func, request=request)

    parameter: param.Parameter
    for parameter in params.values():
        if not isinstance(parameter.spec, tuple(whitelisted_operation_params)):
            raise InvalidParameterSpecification(
                f"Invalid operation parameter specification: {parameter.spec!r}"
            )

    return params


def compose_func(
    request: RequestOptions, func: Callable, arguments: Mapping[str, Any]
) -> None:
    params: Dict[str, param.Parameter] = get_operation_params(func, request=request)

    parameter: param.Parameter
    for parameter in params.values():
        value: Any = arguments[parameter.name]

        compose(request, parameter, value)

    _validate_request_options(request)
