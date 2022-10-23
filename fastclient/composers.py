from dataclasses import dataclass
from typing import (
    Any,
    Generic,
    Mapping,
    Optional,
    Protocol,
    TypeVar,
    Union,
)

import fastapi.encoders
import httpx
from loguru import logger
import param
from pydantic import Required
from pydantic.fields import UndefinedType
import param.parameters
from param.errors import ResolutionError
from param.resolvers import Resolvers

from . import converters
from .converters import Converter
from .composition import factories
from .composition.models import Entry
from .composition.typing import Composer, ComposerFactory
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


def empty_consumer(_: RequestOptions, /) -> None:
    pass


class Resolver(Protocol[P]):
    def __call__(
        self,
        param: P,
        argument: Any,
    ) -> Composer:
        ...


@dataclass
class ParamResolver(Resolver[PA]):
    composer_factory: ComposerFactory[Entry[str, str]]
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

        key: str = param.alias
        value: str = self.converter(argument)

        return self.composer_factory(Entry(key, value))


@dataclass
class ParamsResolver(Resolver[PS], Generic[PS, I, T]):
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
        Query: ParamResolver(
            factories.QueryParamComposer, converters.convert_query_param
        ),
        Header: ParamResolver(factories.HeaderComposer, converters.convert_header),
        Cookie: ParamResolver(factories.CookieComposer, converters.convert_cookie),
        Path: ParamResolver(factories.PathParamComposer, converters.convert_path_param),
        QueryParams: ParamsResolver[QueryParams, QueryParamTypes, httpx.QueryParams](
            parser=Parser(QueryParamTypes),
            composer_factory=factories.QueryParamsComposer,
            converter=converters.convert_query_params,
        ),
        Headers: ParamsResolver[Headers, HeaderTypes, httpx.Headers](
            parser=Parser(HeaderTypes),
            composer_factory=factories.HeadersComposer,
            converter=converters.convert_headers,
        ),
        Cookies: ParamsResolver[Cookies, CookieTypes, httpx.Cookies](
            parser=Parser(CookieTypes),
            composer_factory=factories.CookiesComposer,
            converter=converters.convert_cookies,
        ),
        PathParams: ParamsResolver[PathParams, Mapping[str, Any], Mapping[str, str]](
            parser=Parser(Mapping[str, Any]),
            composer_factory=factories.PathParamsComposer,
            converter=converters.convert_path_params,
        ),
        # NOTE: Currently disabled as broken
        # Body: compose_body,
    }
)

def compose(request: RequestOptions, param: param.parameters.Param, argument: Any) -> None:
    logger.info(
        "Composing param {param!r} with argument {argument!r}",
        param=param,
        argument=argument,
    )

    resolver: Optional[Resolver] = resolvers.get(type(param))

    if resolver is None:
        raise ResolutionError(f"Failed to find composition resolver for param {param!r}")

    logger.info(f"Found composition resolver: {resolver!r}")

    composer: Composer = resolver(param, argument)

    logger.info(f"Applying composer: {composer!r}")

    composer(request)