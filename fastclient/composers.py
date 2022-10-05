import inspect
import urllib.parse
from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping, Protocol, Set, Union

import fastapi.encoders
import param
import pydantic
from param.errors import ResolutionError
from param.manager import ParameterManager
from param.models import Arguments
from param.parameters import ParameterSpecification
from param.resolvers import Resolvers, resolve_param
from param.sentinels import Missing, MissingType

from . import utils
from .errors import IncompatiblePathParameters
from .models import ComposerContext, RequestOptions
from .parameters import (
    Body,
    Cookie,
    Cookies,
    Header,
    Headers,
    Param,
    Params,
    Path,
    PathParams,
    Query,
    QueryParams,
)


class Composer(Protocol):
    def __call__(
        self,
        parameter: param.Parameter[ParameterSpecification],
        context: ComposerContext,
        value: Union[Any, MissingType],
    ):
        ...


def _parse_obj(annotation: Union[MissingType, Any], obj: Any) -> Any:
    if type(obj) is annotation or annotation in (inspect.Parameter.empty, Missing):
        return obj
    else:
        return pydantic.parse_obj_as(annotation, obj)


def _get_alias(parameter: param.Parameter[Param], /) -> str:
    if parameter.default.alias is not None:
        return parameter.default.alias
    else:
        return parameter.default.generate_alias(parameter.name)


def _validate_request_options(request: RequestOptions, /) -> None:
    missing_path_params: Set[str] = utils.get_path_params(
        urllib.parse.unquote(str(request.url))
    )

    # Validate path params are correct
    if missing_path_params:
        raise IncompatiblePathParameters(
            f"Incompatible path params. Missing: {missing_path_params}"
        )


def _compose_param(
    parameter: param.Parameter[Param],
    value: Union[Any, MissingType],
    setter: Callable[[str, Any], Any],
) -> None:
    true_value: Any = resolve_param(parameter, value)

    field_name: str = _get_alias(parameter)

    # If the field is not required and has no value, it can be omitted
    if true_value is None and not parameter.default.required:
        return

    # Convert the value to a string
    string_value: str = _parse_obj(str, true_value)

    # Set the value
    setter(field_name, string_value)


def _compose_params(
    parameter: param.Parameter[Params],
    value: Union[Any, MissingType],
    setter: Callable[[Any], Any],
) -> None:
    true_value: Any = resolve_param(parameter, value)

    setter(true_value)


resolvers: Resolvers[Composer] = Resolvers()


@resolvers(Query)
def compose_query_param(
    parameter: param.Parameter[Query],
    context: ComposerContext,
    value: Union[Any, MissingType],
) -> None:
    return _compose_param(parameter, value, context.request.add_query_param)


@resolvers(Header)
def compose_header(
    parameter: param.Parameter[Header],
    context: ComposerContext,
    value: Union[Any, MissingType],
) -> None:
    return _compose_param(parameter, value, context.request.add_header)


@resolvers(Cookie)
def compose_cookie(
    parameter: param.Parameter[Cookie],
    context: ComposerContext,
    value: Union[Any, MissingType],
) -> None:
    return _compose_param(parameter, value, context.request.add_cookie)


@resolvers(Path)
def compose_path_param(
    parameter: param.Parameter[Path],
    context: ComposerContext,
    value: Union[Any, MissingType],
) -> None:
    return _compose_param(parameter, value, context.request.add_path_param)


@resolvers(Body)
def compose_body(
    parameter: param.Parameter[Body],
    context: ComposerContext,
    value: Union[Any, MissingType],
) -> None:
    true_value: Any

    if value is not Missing:
        true_value = value
    elif parameter.default.has_default():
        true_value = parameter.default.get_default()
    else:
        raise ResolutionError(
            f"Failed to compose parameter: {parameter!r} - No default and no value provided"
        )

    field_name: str = _get_alias(parameter)

    # If the field is not required and has no value, it can be omitted
    if true_value is None and not parameter.default.required:
        return

    json_value: Any = fastapi.encoders.jsonable_encoder(true_value)

    total_body_params: int = len(
        [
            parameter
            for parameter in context.parameters.values()
            if type(parameter.default) is Body
        ]
    )

    embed: bool = parameter.default.embed

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


@resolvers(QueryParams)
def compose_query_params(
    parameter: param.Parameter[QueryParams],
    context: ComposerContext,
    value: Union[Any, MissingType],
) -> None:
    return _compose_params(parameter, value, context.request.add_query_params)


@resolvers(Headers)
def compose_headers(
    parameter: param.Parameter[Headers],
    context: ComposerContext,
    value: Union[Any, MissingType],
) -> None:
    return _compose_params(parameter, value, context.request.add_headers)


@resolvers(Cookies)
def compose_cookies(
    parameter: param.Parameter[Cookie],
    context: ComposerContext,
    value: Union[Any, MissingType],
) -> None:
    return _compose_params(parameter, value, context.request.add_cookies)


@resolvers(PathParams)
def compose_path_params(
    parameter: param.Parameter[PathParams],
    context: ComposerContext,
    value: Union[Any, MissingType],
) -> None:
    return _compose_params(parameter, value, context.request.add_path_params)


@dataclass
class CompositionParameterManager(ParameterManager[Composer]):
    resolvers: Resolvers[Composer]
    request: RequestOptions

    # NOTE: Composition parameter inference should be much more advanced than this.
    # `api.get_params` contains the current inference logic that should be used.
    def infer_spec(self, parameter: inspect.Parameter, /) -> ParameterSpecification:
        return Query(
            default=parameter.default
            if parameter.default is not inspect.Parameter.empty
            else Missing
        )

    def resolve_arguments(
        self,
        arguments: Dict[
            param.Parameter[ParameterSpecification], Union[Any, MissingType]
        ],
        /,
    ) -> Dict[str, Any]:
        resolved_arguments: Dict[str, Any] = {}

        parameters: Dict[str, param.Parameter[ParameterSpecification]] = {
            parameter.name: parameter for parameter in arguments.keys()
        }

        context: ComposerContext = ComposerContext(
            request=self.request, parameters=parameters
        )

        parameter: param.Parameter[ParameterSpecification]
        argument: Union[Any, MissingType]
        for parameter, argument in arguments.items():
            composer: Composer = self.get_resolver(type(parameter.default))

            resolved_arguments[parameter.name] = composer(parameter, context, argument)

        return resolved_arguments


def compose_func(
    request: RequestOptions, func: Callable, arguments: Mapping[str, Any]
) -> None:
    manager: ParameterManager[Composer] = CompositionParameterManager(
        resolvers=resolvers,
        request=request,
    )

    # NOTE: `params` should complain if a param spec doesn't have a specified resolver.
    # It does not currently do this.
    manager.get_arguments(func, Arguments(kwargs=arguments))

    _validate_request_options(request)
