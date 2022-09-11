from dataclasses import dataclass
import inspect
import urllib.parse
from typing import Any, Callable, Dict, Mapping, Set, Union

import fastapi.encoders
import param
from param.errors import ResolutionError
from param.parameters import ParameterSpecification
from param.models import Arguments
from param.manager import ParameterManager
from param.resolvers import Resolvers
from param.sentinels import Missing, MissingType
import pydantic

from . import utils
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


def _parse_obj(annotation: Union[MissingType, Any], obj: Any) -> Any:
    if type(obj) is annotation or annotation in (inspect._empty, Missing):
        return obj

    return pydantic.parse_obj_as(annotation, obj)


def _get_alias(parameter: param.Parameter[Param], /) -> str:
    if parameter.spec.alias is not None:
        return parameter.spec.alias
    else:
        return parameter.spec.generate_alias(parameter.name)


def _compose_param(
    parameter: param.Parameter[Param],
    value: Union[Any, MissingType],
    setter: Callable[[str, Any], Any],
) -> None:
    true_value: Any

    if value is not Missing:
        true_value = value
    elif parameter.spec.has_default():
        true_value = parameter.spec.get_default()
    else:
        raise ResolutionError(
            f"Failed to compose parameter: {parameter!r} - No default and no value provided"
        )

    field_name: str = _get_alias(parameter)

    # If the field is not required and has no value, it can be omitted
    if true_value is None and not parameter.spec.required:
        return

    # Convert the value to a string
    string_value: str = _parse_obj(str, true_value)

    # Set the value
    setter(field_name, string_value)


def compose_query_param(
    parameter: param.Parameter[Query],
    context: ComposerContext,
    value: Union[Any, MissingType],
) -> None:
    return _compose_param(parameter, value, context.request.add_query_param)


def compose_header(
    parameter: param.Parameter[Header],
    context: ComposerContext,
    value: Union[Any, MissingType],
) -> None:
    return _compose_param(parameter, value, context.request.add_header)


def compose_cookie(
    parameter: param.Parameter[Cookie],
    context: ComposerContext,
    value: Union[Any, MissingType],
) -> None:
    return _compose_param(parameter, value, context.request.add_cookie)


def compose_path_param(
    parameter: param.Parameter[Path],
    context: ComposerContext,
    value: Union[Any, MissingType],
) -> None:
    return _compose_param(parameter, value, context.request.add_path_param)


def compose_body(
    parameter: param.Parameter[Body],
    context: ComposerContext,
    value: Union[Any, MissingType],
) -> None:
    true_value: Any

    if value is not Missing:
        true_value = value
    elif parameter.spec.has_default():
        true_value = parameter.spec.get_default()
    else:
        raise ResolutionError(
            f"Failed to compose parameter: {parameter!r} - No default and no value provided"
        )

    field_name: str = _get_alias(parameter)

    # If the field is not required and has no value, it can be omitted
    if true_value is None and not parameter.spec.required:
        return

    json_value: Any = fastapi.encoders.jsonable_encoder(true_value)

    total_body_params: int = len(
        [
            parameter
            for parameter in context.parameters.values()
            if type(parameter.spec) is Body
        ]
    )

    embed: bool = parameter.spec.embed

    if total_body_params > 1:
        embed = True

    if embed:
        json_value = {field_name: json_value}

    # If there's only one body param, or this param shouln't be embedded in any pre-existing json,
    # make it the entire JSON request body
    if context.request.json is None or not embed:
        context.request.json = json_value
    else:
        context.request.json.update(json_value)


def _compose_params(
    parameter: param.Parameter[Params],
    value: Union[Any, MissingType],
    setter: Callable[[Any], Any],
) -> None:
    true_value: Any

    if value is not Missing:
        true_value = value
    elif parameter.spec.has_default():
        true_value = parameter.spec.get_default()
    else:
        raise ResolutionError(
            f"Failed to compose parameter: {parameter!r} - No default and no value provided"
        )

    setter(true_value)


def compose_query_params(
    parameter: param.Parameter[QueryParams],
    context: ComposerContext,
    value: Union[Any, MissingType],
) -> None:
    return _compose_params(parameter, value, context.request.add_query_params)


def compose_headers(
    parameter: param.Parameter[Headers],
    context: ComposerContext,
    value: Union[Any, MissingType],
) -> None:
    return _compose_params(parameter, value, context.request.add_headers)


def compose_cookies(
    parameter: param.Parameter[Cookie],
    context: ComposerContext,
    value: Union[Any, MissingType],
) -> None:
    return _compose_params(parameter, value, context.request.add_cookies)


def compose_path_params(
    parameter: param.Parameter[PathParams],
    context: ComposerContext,
    value: Union[Any, MissingType],
) -> None:
    return _compose_params(parameter, value, context.request.add_path_params)


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
    request: RequestOptions
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
        return {
            parameter: ComposerContext(request=self.request, parameters=parameters)
            for parameter in parameters
        }


def compose_func(
    request: RequestOptions, func: Callable, arguments: Mapping[str, Any]
) -> None:
    manager: ParameterManager[ComposerContext] = CompositionParameterManager(
        resolvers=Resolvers(
            {
                Query: compose_query_param,
                Header: compose_header,
                Cookie: compose_cookie,
                Path: compose_path_param,
                Body: compose_body,
                QueryParams: compose_query_params,
                Headers: compose_headers,
                Cookies: compose_cookies,
                PathParams: compose_path_params,
            }
        ),
        request=request,
        infer=True,
    )

    # NOTE: `params` should complain if a param spec doesn't have a specified resolver.
    # It does not currently do this.
    manager.get_arguments(func, Arguments(kwargs=arguments))

    _validate_request_options(request)
