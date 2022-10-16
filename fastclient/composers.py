from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, Optional, Protocol, Union

import fastapi.encoders
import param
from pydantic import Required
from pydantic.fields import UndefinedType
from param import Resolvable
import param.parameters
from param.errors import ResolutionError
from param.manager import ParameterManager
from param.models import Arguments
from param.resolvers import Resolvers, resolve_param

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
        request: RequestOptions,
        param: param.parameters.Param,
        value: Union[Any, UndefinedType],
    ):
        ...


# TODO: Implement me...
class ParamComposer(Composer):
    def __call__(
        self,
        request: RequestOptions,
        param: param.parameters.Param,
        value: Union[Any, UndefinedType],
    ):
        ...


def _compose_param(
    param: Param,
    value: Union[Any, UndefinedType],
    setter: Callable[[str, Any], Any],
) -> None:
    true_value: Any = resolve_param(param, value)

    if param.alias is None:
        raise ResolutionError("Cannot compose `Param` with no alias")

    # If the param is not required and has no value, it can be omitted
    if true_value is None and param.default is not Required:
        return

    # Set the value
    setter(param.alias, true_value)


def _compose_params(
    param: Params,
    value: Union[Any, UndefinedType],
    setter: Callable[[Any], Any],
) -> None:
    true_value: Any = resolve_param(param, value)

    setter(true_value)


resolvers: Resolvers[Composer] = Resolvers()


@resolvers(Query)
def compose_query_param(
    request: RequestOptions,
    param: Query,
    value: Union[Any, UndefinedType],
) -> None:
    return _compose_param(param, value, request.add_query_param)


@resolvers(Header)
def compose_header(
    request: RequestOptions,
    param: Header,
    value: Union[Any, UndefinedType],
) -> None:
    return _compose_param(param, value, request.add_header)


@resolvers(Cookie)
def compose_cookie(
    request: RequestOptions,
    param: Cookie,
    value: Union[Any, UndefinedType],
) -> None:
    return _compose_param(param, value, request.add_cookie)


@resolvers(Path)
def compose_path_param(
    request: RequestOptions,
    param: Path,
    value: Union[Any, UndefinedType],
) -> None:
    return _compose_param(param, value, request.add_path_param)


@resolvers(QueryParams)
def compose_query_params(
    request: RequestOptions,
    param: QueryParams,
    value: Union[Any, UndefinedType],
) -> None:
    return _compose_params(param, value, request.add_query_params)


@resolvers(Headers)
def compose_headers(
    request: RequestOptions,
    param: Headers,
    value: Union[Any, UndefinedType],
) -> None:
    return _compose_params(param, value, request.add_headers)


@resolvers(Cookies)
def compose_cookies(
    request: RequestOptions,
    param: Cookies,
    value: Union[Any, UndefinedType],
) -> None:
    return _compose_params(param, value, request.add_cookies)


@resolvers(PathParams)
def compose_path_params(
    request: RequestOptions,
    param: PathParams,
    value: Union[Any, UndefinedType],
) -> None:
    return _compose_params(param, value, request.add_path_params)


# NOTE: This resolver is currently untested
# TODO: Add some middleware that sets/unsets `embed` as appropriate
@resolvers(Body)
def compose_body(
    parameter: param.Parameter,
    param: Body,
    value: Union[Any, UndefinedType],
    context: ComposerContext,
) -> None:
    true_value: Any = resolve_param(parameter, value)

    # If the param is not required and has no value, it can be omitted
    if true_value is None and param.default is not Required:
        return

    json_value: Any = fastapi.encoders.jsonable_encoder(true_value)

    total_body_params: int = len(
        [
            parameter
            for parameter in context.parameters.values()
            if type(parameter.default) is Body
        ]
    )

    embed: bool = param.embed

    if total_body_params > 1:
        embed = True

    if embed:
        if param.alias is None:
            raise ResolutionError("Cannot embed `Body` with no alias")

        json_value = {param.alias: json_value}

    # If there's only one body param, or this param shouln't be embedded in any pre-existing json,
    # make it the entire JSON request body
    if context.request.json is None or not embed:
        context.request.json = json_value
    else:
        context.request.json.update(json_value)


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
        resolved_arguments: Dict[str, Any] = {}

        # parameters: Dict[str, param.Parameter] = {
        #     resolvable.parameter.name: resolvable.parameter
        #     for resolvable in resolvables
        # }

        resolvable: Resolvable
        for resolvable in resolvables:
            parameter: param.Parameter = resolvable.parameter
            field: param.parameters.Param = resolvable.field
            value: Union[Any, UndefinedType] = resolvable.argument

            composer: Composer = self.get_resolver(type(field))

            resolved_arguments[parameter.name] = composer(self.request, field, value)

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

    request.validate()
