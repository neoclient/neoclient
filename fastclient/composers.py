from dataclasses import dataclass
from typing import (
    Any,
    Optional,
    Protocol,
    TypeVar,
)

from loguru import logger
import param
from pydantic import Required
import param.parameters
from param.errors import ResolutionError
from param.resolvers import Resolvers
from param.typing import Function

from . import converters
from .composition import factories, wrappers
from .composition.models import Entry
from .composition.typing import RequestConsumer, RequestConsumerFactory
from .models import RequestOptions
from .parameters import (
    Cookie,
    Cookies,
    Header,
    Headers,
    Path,
    Param,
    PathParams,
    Query,
    QueryParams,
)
from .parsing import parse_obj_as
from .types import (
    QueryParamTypes,
    HeaderTypes,
    CookieTypes,
    PathParamTypes,
)


P = TypeVar("P", contravariant=True, bound=param.parameters.Param)
PA = TypeVar("PA", contravariant=True, bound=Param)


def noop_consumer(_: RequestOptions, /) -> None:
    pass


class Composer(Protocol[P]):
    def __call__(
        self,
        param: P,
        argument: Any,
    ) -> RequestConsumer:
        ...

composers: Resolvers[Composer] = Resolvers()


@dataclass
class ParamComposer(Composer[PA]):
    composer_factory: RequestConsumerFactory[Entry[str, str]]
    converter: Function[Any, str]

    def __call__(
        self,
        param: PA,
        argument: Any,
    ) -> RequestConsumer:
        if param.alias is None:
            raise ResolutionError("Cannot compose `Param` with no alias")

        if argument is None and param.default is not Required:
            return noop_consumer

        key: str = param.alias
        value: str = self.converter(argument)

        return self.composer_factory(Entry(key, value))

@composers(QueryParams)
def compose_query_params(
    param: QueryParams,
    argument: Any,
) -> RequestConsumer:
    query_params: QueryParamTypes = parse_obj_as(QueryParamTypes, argument)

    return wrappers.query_params(query_params)


@composers(Headers)
def compose_headers(
    param: Headers,
    argument: Any,
) -> RequestConsumer:
    headers: HeaderTypes = parse_obj_as(HeaderTypes, argument)

    return wrappers.headers(headers)


@composers(Cookies)
def compose_cookies(
    param: Cookies,
    argument: Any,
) -> RequestConsumer:
    cookies: CookieTypes = parse_obj_as(CookieTypes, argument)

    return wrappers.cookies(cookies)


@composers(PathParams)
def compose_path_params(
    param: PathParams,
    argument: Any,
) -> RequestConsumer:
    path_params: PathParamTypes = parse_obj_as(PathParamTypes, argument)

    return wrappers.path_params(path_params)


# NOTE: This resolver is currently untested
# TODO: Add some middleware that sets/unsets `embed` as appropriate
"""
def compose_body(
    param: P,
    argument: Any,
) -> RequestConsumer:
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
"""


composers.update(
    {
        Query: ParamComposer(
            factories.QueryParamComposer, converters.convert_query_param
        ),
        Header: ParamComposer(factories.HeaderComposer, converters.convert_header),
        Cookie: ParamComposer(factories.CookieComposer, converters.convert_cookie),
        Path: ParamComposer(factories.PathParamComposer, converters.convert_path_param),
        # QueryParams: compose_query_params,
        # Headers: compose_headers,
        # Cookies: compose_cookies,
        # PathParams: compose_path_params,
        # QueryParams: ParamsComposer[QueryParams, QueryParamTypes, httpx.QueryParams](
        #     parser=Parser(QueryParamTypes),
        #     composer_factory=factories.QueryParamsComposer,
        #     converter=converters.convert_query_params,
        # ),
        # Headers: ParamsComposer[Headers, HeaderTypes, httpx.Headers](
        #     parser=Parser(HeaderTypes),
        #     composer_factory=factories.HeadersComposer,
        #     converter=converters.convert_headers,
        # ),
        # Cookies: ParamsComposer[Cookies, CookieTypes, httpx.Cookies](
        #     parser=Parser(CookieTypes),
        #     composer_factory=factories.CookiesComposer,
        #     converter=converters.convert_cookies,
        # ),
        # PathParams: ParamsComposer[PathParams, Mapping[str, Any], Mapping[str, str]](
        #     parser=Parser(Mapping[str, Any]),
        #     composer_factory=factories.PathParamsComposer,
        #     converter=converters.convert_path_params,
        # ),
        # NOTE: Currently disabled as broken
        # Body: compose_body,
    }
)


def compose(
    request: RequestOptions, param: param.parameters.Param, argument: Any
) -> None:
    logger.info(
        "Composing param {param!r} with argument {argument!r}",
        param=param,
        argument=argument,
    )

    composer: Optional[Composer] = composers.get(type(param))

    if composer is None:
        raise ResolutionError(
            f"Failed to find composition resolver for param {param!r}"
        )

    logger.info(f"Found composition resolver: {composer!r}")

    composer: RequestConsumer = composer(param, argument)

    logger.info(f"Applying composer: {composer!r}")

    composer(request)
