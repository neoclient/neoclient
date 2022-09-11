import dataclasses
from dataclasses import dataclass
import inspect
import urllib.parse
from typing import Any, Callable, Dict, Mapping, Set, Union

import fastapi.encoders
import httpx
import param
from param.parameters import ParameterSpecification
from param.models import Arguments
from param.manager import ParameterManager
from param.resolvers import Resolvers
from param.sentinels import Missing, MissingType
import pydantic

from . import utils
from .enums import ParamType
from .errors import IncompatiblePathParameters
from .models import ComposerContext, RequestOptions
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


def _parse_obj(annotation: Union[MissingType, Any], obj: Any) -> Any:
    if type(obj) is annotation or annotation in (inspect._empty, Missing):
        return obj

    return pydantic.parse_obj_as(annotation, obj)


def compose_query_param(request: RequestOptions, param: Query, value: str) -> None:
    print("compose_query_param:", request, param, value)

    if param.alias is None:
        raise Exception(f"Cannot compose param {param!r} if it has no alias")

    resolved_value: str = value if value is not Missing else param.get_default()

    request.add_query_param(param.alias, resolved_value)


def compose_header(request: RequestOptions, param: Header, value: str) -> None:
    if param.alias is None:
        raise Exception(f"Cannot compose param {param!r} if it has no alias")

    resolved_value: str = value if value is not Missing else param.get_default()

    request.add_header(param.alias, resolved_value)


def compose_cookie(request: RequestOptions, param: Cookie, value: str) -> None:
    if param.alias is None:
        raise Exception(f"Cannot compose param {param!r} if it has no alias")

    resolved_value: str = value if value is not Missing else param.get_default()

    request.add_cookie(param.alias, resolved_value)


def compose_path_param(request: RequestOptions, param: Path, value: str) -> None:
    if param.alias is None:
        raise Exception(f"Cannot compose param {param!r} if it has no alias")

    resolved_value: str = value if value is not Missing else param.get_default()

    request.add_path_param(param.alias, resolved_value)


def compose_param(
    parameter: param.Parameter, context: ComposerContext, value: Union[Any, MissingType]
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

        compose_query_param(context.request, spec, value)
    elif spec.type is ParamType.HEADER:
        # Convert the value
        value = _parse_obj(str, value)

        compose_header(context.request, spec, value)
    elif spec.type is ParamType.COOKIE:
        # Convert the value
        value = _parse_obj(str, value)

        compose_cookie(context.request, spec, value)
    elif spec.type is ParamType.PATH:
        # Convert the value
        value = _parse_obj(str, value)

        compose_path_param(context.request, spec, value)
    else:
        raise Exception(f"Unknown ParamType: {spec.type!r}")


def compose_body(
    parameter: param.Parameter, context: ComposerContext, value: Union[Any, MissingType]
) -> None:
    if not isinstance(parameter.spec, Body):
        raise Exception("Parameter is not a Body")
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

    resolved_value: Any = fastapi.encoders.jsonable_encoder(
        value if value is not None else spec.get_default()
    )

    if spec.embed:
        if spec.alias is None:
            raise Exception(f"Cannot embed body param {spec!r} if it has no alias")

        resolved_value = {spec.alias: resolved_value}

    # If there's only one body param, or this param shouln't be embedded in any pre-existing json,
    # make it the entire JSON request body
    if context.request.json is None or not spec.embed:
        context.request.json = resolved_value
    else:
        context.request.json.update(resolved_value)


def compose_query_params(
    request: RequestOptions,
    param: QueryParams,
    value: QueryParamTypes,
) -> None:
    resolved_value: httpx.QueryParams = (
        httpx.QueryParams(value) if value is not Missing else param.get_default()
    )

    request.add_query_params(resolved_value)


def compose_headers(
    request: RequestOptions,
    param: Headers,
    value: HeaderTypes,
) -> None:
    resolved_value: httpx.Headers = (
        httpx.Headers(value) if value is not Missing else param.get_default()
    )

    request.add_headers(resolved_value)


def compose_cookies(
    request: RequestOptions,
    param: Cookies,
    value: CookieTypes,
) -> None:
    resolved_value: httpx.Cookies = (
        httpx.Cookies(value) if value is not Missing else param.get_default()
    )

    request.add_cookies(resolved_value)


def compose_path_params(
    request: RequestOptions,
    param: Cookies,
    value: Dict[str, Any],
) -> None:
    resolved_value: Dict[str, Any] = (
        value if value is not Missing else param.get_default()
    )

    request.add_path_params(resolved_value)


def compose_params(
    parameter: param.Parameter, context: ComposerContext, value: Union[Any, MissingType]
) -> None:
    spec: Params

    if not isinstance(parameter.spec, Params):
        raise Exception("Parameter is not a Params")
    else:
        spec = parameter.spec

    if spec.type is ParamType.QUERY:
        compose_query_params(context.request, spec, value)
    elif spec.type is ParamType.HEADER:
        compose_headers(context.request, spec, value)
    elif spec.type is ParamType.COOKIE:
        compose_cookies(context.request, spec, value)
    elif spec.type is ParamType.PATH:
        compose_path_params(context.request, spec, value)
    else:
        raise Exception(f"Unknown multi-param: {spec.type!r}")


def _validate_request_options(request: RequestOptions, /) -> None:
    missing_path_params: Set[str] = utils.get_path_params(
        urllib.parse.unquote(str(request.url))
    )

    # Validate path params are correct
    if missing_path_params:
        raise IncompatiblePathParameters(
            f"Incompatible path params. Missing: {missing_path_params}"
        )


@dataclass
class CompositionParameterManager(ParameterManager[ComposerContext]):
    resolvers: Resolvers[ComposerContext]
    context: ComposerContext
    infer: bool = True

    # NOTE: Composition parameter inference should be much more advanced than this.
    # `api.get_params` contains the current inference logic that should be used.
    def infer_parameter(
        self, parameter: inspect.Parameter, /
    ) -> ParameterSpecification:
        return Query(
            default=parameter.default
            if parameter.default is not inspect._empty
            else Missing
        )

    def build_contexts(
        self, parameters: Dict[str, param.Parameter], arguments: Dict[str, Any]
    ) -> Dict[str, ComposerContext]:
        return {parameter: self.context for parameter in parameters}


def compose_func(
    request: RequestOptions, func: Callable, arguments: Mapping[str, Any]
) -> None:
    manager: ParameterManager[ComposerContext] = CompositionParameterManager(
        resolvers=Resolvers(
            {
                Query: compose_param,
                Header: compose_param,
                Cookie: compose_param,
                Path: compose_param,
                Body: compose_body,
                QueryParams: compose_params,
                Headers: compose_params,
                Cookies: compose_params,
                PathParams: compose_params,
            }
        ),
        context=ComposerContext(request=request),
        infer=True,
    )

    # NOTE: `params` should complain if a param spec doesn't have a specified resolver.
    # It does not currently do this.
    manager.get_arguments(func, Arguments(kwargs=arguments))

    _validate_request_options(request)
