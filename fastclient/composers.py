from dataclasses import dataclass
from typing import (
    Any,
    Generic,
    Protocol,
    TypeVar,
    Union,
)

import fastapi.encoders
import param
from pydantic import Required
from pydantic.fields import UndefinedType
import param.parameters
from param.errors import ResolutionError
from param.resolvers import Resolvers
from param.typing import Consumer

from .composition import factories
from .composition.typing import Composer
from .models import ComposerContext, RequestOptions
from .parameters import (
    Body,
    Cookie,
    Cookies,
    Header,
    Headers,
    Path,
    Param,
    Params,
    PathParams,
    Query,
    QueryParams,
)


P = TypeVar("P", contravariant=True, bound=param.parameters.Param)
T = TypeVar("T", contravariant=True)


class ParamComposerFactory(Protocol):
    def __call__(self, key: str, value: Any) -> Composer:
        ...


class ComposerFactory(Protocol[T]):
    def __call__(self, t: T, /) -> Composer:
        ...


class Resolver(Protocol[P]):
    def __call__(
        self,
        param: P,
        argument: Any,
    ) -> Composer:
        ...


class ParamsSetter(Protocol):
    def __call__(self, request: RequestOptions, value: Any, /) -> None:
        ...


@dataclass
class ParamsComposer(Resolver[Params], Generic[T]):
    composer_factory: ComposerFactory[T]

    def __call__(
        self,
        _: Params,
        argument: Any,
    ) -> Consumer:
        return self.composer_factory(argument)


@dataclass
class ParamComposer(Resolver[Param]):
    composer_factory: ParamComposerFactory

    def __call__(
        self,
        param: Param,
        argument: Any,
    ) -> Consumer:
        if param.alias is None:
            raise ResolutionError("Cannot compose `Param` with no alias")

        if argument is None and param.default is not Required:
            return empty_consumer

        return self.composer_factory(param.alias, argument)


def empty_consumer(_: RequestOptions, /) -> None:
    pass


# NOTE: This resolver is currently untested
# TODO: Add some middleware that sets/unsets `embed` as appropriate
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


resolvers: Resolvers[Resolver] = Resolvers(
    {
        Query: ParamComposer(factories.QueryParamComposer),
        Header: ParamComposer(factories.HeaderComposer),
        Cookie: ParamComposer(factories.CookieComposer),
        Path: ParamComposer(factories.PathParamComposer),
        QueryParams: ParamsComposer(factories.QueryParamsComposer),
        Headers: ParamsComposer(factories.HeadersComposer),
        Cookies: ParamsComposer(factories.CookiesComposer),
        PathParams: ParamsComposer(factories.PathParamsComposer),
        # NOTE: Currently disabled as broken
        # Body: compose_body,
    }
)
