from dataclasses import dataclass
from typing import (
    Any,
    Generic,
    Mapping,
    Protocol,
    TypeVar,
    Union,
)

import fastapi.encoders
import httpx
import param
from pydantic import Required
from pydantic.fields import UndefinedType
import param.parameters
from param.errors import ResolutionError
from param.resolvers import Resolvers

from . import converters
from .converters import Converter
from .composition import composers
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
from .parsing import Parser
from .types import (
    QueryParamTypes,
    HeaderTypes,
    CookieTypes,
)


P = TypeVar("P", contravariant=True, bound=param.parameters.Param)
PA = TypeVar("PA", contravariant=True, bound=Param)
PS = TypeVar("PS", contravariant=True, bound=Params)
T = TypeVar("T", contravariant=True)
I = TypeVar("I")


class ParamComposerFactory(Protocol):
    def __call__(self, key: str, value: str) -> Composer:
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
class ParamsComposer(Resolver[PS], Generic[PS, I, T]):
    parser: Parser[I]
    converter: Converter[I, T]
    composer_factory: ComposerFactory[T]

    def __call__(
        self,
        _: PS,
        argument: Any,
    ) -> Composer:
        argument_parsed: I = self.parser(argument)
        argument_converted: T = self.converter(argument_parsed)

        return self.composer_factory(argument_converted)


@dataclass
class ParamComposer(Resolver[PA]):
    composer_factory: ParamComposerFactory
    converter: Converter[Any, str]

    def __call__(
        self,
        param: PA,
        argument: Any,
    ) -> Composer:
        if param.alias is None:
            raise ResolutionError("Cannot compose `Param` with no alias")

        if argument is None and param.default is not Required:
            return empty_consumer

        return self.composer_factory(param.alias, self.converter(argument))


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
        Query: ParamComposer(
            composers.QueryParamComposer, converters.convert_query_param
        ),
        Header: ParamComposer(composers.HeaderComposer, converters.convert_header),
        Cookie: ParamComposer(composers.CookieComposer, converters.convert_cookie),
        Path: ParamComposer(composers.PathParamComposer, converters.convert_path_param),
        QueryParams: ParamsComposer[QueryParams, QueryParamTypes, httpx.QueryParams](
            parser=Parser(QueryParamTypes),
            composer_factory=composers.QueryParamsComposer,
            converter=converters.convert_query_params,
        ),
        Headers: ParamsComposer[Headers, HeaderTypes, httpx.Headers](
            parser=Parser(HeaderTypes),
            composer_factory=composers.HeadersComposer,
            converter=converters.convert_headers,
        ),
        Cookies: ParamsComposer[Cookies, CookieTypes, httpx.Cookies](
            parser=Parser(CookieTypes),
            composer_factory=composers.CookiesComposer,
            converter=converters.convert_cookies,
        ),
        PathParams: ParamsComposer[PathParams, Mapping[str, Any], Mapping[str, str]](
            parser=Parser(Mapping[str, Any]),
            composer_factory=composers.PathParamsComposer,
            converter=converters.convert_path_params,
        ),
        # NOTE: Currently disabled as broken
        # Body: compose_body,
    }
)
