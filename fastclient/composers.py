import inspect
import urllib.parse
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, Optional, Protocol, Set, Union

import fastapi.encoders
import param
import pydantic
from pydantic import Required
from pydantic.fields import Undefined, UndefinedType
from param import Resolvable
import param.parameters
from param.errors import ResolutionError
from param.manager import ParameterManager
from param.models import Arguments
from param.resolvers import Resolvers, resolve_param

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
        parameter: param.Parameter,
        field: param.parameters.Param,
        value: Union[Any, UndefinedType],
        context: ComposerContext,
    ):
        ...


def _parse_obj(annotation: Union[UndefinedType, Any], obj: Any) -> Any:
    if type(obj) is annotation or isinstance(annotation, UndefinedType):
        return obj
    else:
        return pydantic.parse_obj_as(annotation, obj)


def _get_alias(field: Param, parameter_name: str, /) -> str:
    if field.alias is not None:
        return field.alias
    else:
        return field.generate_alias(parameter_name)


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
    parameter: param.Parameter,
    field: Param,
    value: Union[Any, UndefinedType],
    setter: Callable[[str, Any], Any],
) -> None:
    true_value: Any = resolve_param(
        Resolvable(
            parameter=parameter,
            field=field,
            argument=value,
        )
    )

    field_name: str = _get_alias(field, parameter.name)

    # If the field is not required and has no value, it can be omitted
    if true_value is None and field.default is not Required:
        return

    # Convert the value to a string
    string_value: str = _parse_obj(str, true_value)

    # Set the value
    setter(field_name, string_value)


def _compose_params(
    parameter: param.Parameter,
    value: Union[Any, UndefinedType],
    setter: Callable[[Any], Any],
) -> None:
    if not isinstance(parameter.default, Params):
        raise Exception("Cannot compose non-params")

    true_value: Any = resolve_param(parameter, value)

    setter(true_value)


resolvers: Resolvers[Composer] = Resolvers()


@resolvers(Query)
def compose_query_param(
    parameter: param.Parameter,
    field: Query,
    value: Union[Any, UndefinedType],
    context: ComposerContext,
) -> None:
    return _compose_param(parameter, field, value, context.request.add_query_param)


@resolvers(Header)
def compose_header(
    parameter: param.Parameter,
    field: Header,
    value: Union[Any, UndefinedType],
    context: ComposerContext,
) -> None:
    return _compose_param(parameter, field, value, context.request.add_header)


@resolvers(Cookie)
def compose_cookie(
    parameter: param.Parameter,
    field: Cookie,
    value: Union[Any, UndefinedType],
    context: ComposerContext,
) -> None:
    return _compose_param(parameter, field, value, context.request.add_cookie)


@resolvers(Path)
def compose_path_param(
    parameter: param.Parameter,
    field: Path,
    value: Union[Any, UndefinedType],
    context: ComposerContext,
) -> None:
    return _compose_param(parameter, field, value, context.request.add_path_param)


@resolvers(Body)
def compose_body(
    parameter: param.Parameter,
    field: Body,
    value: Union[Any, UndefinedType],
    context: ComposerContext,
) -> None:
    true_value: Any

    if value is not Undefined:
        true_value = value
    elif field.has_default():
        true_value = field.get_default()
    else:
        raise ResolutionError(
            f"Failed to compose parameter: {parameter!r} - No default and no value provided"
        )

    field_name: str = _get_alias(field, parameter.name)

    # If the field is not required and has no value, it can be omitted
    if true_value is None and field.default is not Required:
        return

    json_value: Any = fastapi.encoders.jsonable_encoder(true_value)

    total_body_params: int = len(
        [
            parameter
            for parameter in context.parameters.values()
            if type(parameter.default) is Body
        ]
    )

    embed: bool = field.embed

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
    parameter: param.Parameter,
    value: Union[Any, UndefinedType],
    context: ComposerContext,
) -> None:
    return _compose_params(parameter, value, context.request.add_query_params)


@resolvers(Headers)
def compose_headers(
    parameter: param.Parameter,
    value: Union[Any, UndefinedType],
    context: ComposerContext,
) -> None:
    return _compose_params(parameter, value, context.request.add_headers)


@resolvers(Cookies)
def compose_cookies(
    parameter: param.Parameter,
    value: Union[Any, UndefinedType],
    context: ComposerContext,
) -> None:
    return _compose_params(parameter, value, context.request.add_cookies)


@resolvers(PathParams)
def compose_path_params(
    parameter: param.Parameter,
    value: Union[Any, UndefinedType],
    context: ComposerContext,
) -> None:
    return _compose_params(parameter, value, context.request.add_path_params)


@dataclass
class CompositionParameterManager(ParameterManager[Composer]):
    resolvers: Resolvers[Composer]
    request: RequestOptions

    # NOTE: Composition parameter inference should be much more advanced than this.
    # `api.get_params` contains the current inference logic that should be used.
    def get_param(self, parameter: param.Parameter, /) -> param.parameters.Param:
        param: Optional[param.parameters.Param] = super().get_param(parameter)

        if param is not None:
            return param
        else:
            return Query(
                default=parameter.default,
            )

    def resolve_all(
        self,
        resolvables: Iterable[Resolvable],
        /,
    ) -> Dict[str, Any]:
        print("resolve_all:", resolvables)

        resolved_arguments: Dict[str, Any] = {}

        parameters: Dict[str, param.Parameter] = {
            resolvable.parameter.name: resolvable.parameter
            for resolvable in resolvables
        }

        context: ComposerContext = ComposerContext(
            request=self.request, parameters=parameters
        )

        resolvable: Resolvable
        for resolvable in resolvables:
            parameter: param.Parameter = resolvable.parameter
            field: param.parameters.Param = resolvable.field
            argument: Union[Any, UndefinedType] = resolvable.argument

            composer: Composer = self.get_resolver(type(field))

            # print("Composing:", composer, parameter, field, argument, context)

            resolved_arguments[parameter.name] = composer(
                parameter, field, argument, context
            )

        return resolved_arguments


def compose_func(
    request: RequestOptions, func: Callable, arguments: Dict[str, Any]
) -> None:
    manager: ParameterManager[Composer] = CompositionParameterManager(
        resolvers=resolvers,
        request=request,
    )

    # NOTE: `params` should complain if a param spec doesn't have a specified resolver.
    # It does not currently do this.
    manager.get_arguments(func, Arguments(kwargs=arguments))

    _validate_request_options(request)
