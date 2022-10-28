from dataclasses import dataclass
from typing import Any, Optional, Protocol, Type, TypeVar, Generic

import param
import param.parameters
from loguru import logger
from param.errors import ResolutionError
from pydantic import Required
from roster import Register

from .consumers import (
    QueryParamConsumer,
    HeaderConsumer,
    CookieConsumer,
    PathParamConsumer,
    QueryParamsConsumer,
    HeadersConsumer,
    CookiesConsumer,
    PathParamsConsumer,
)
from .typing import RequestConsumer, RequestConsumerFactory
from .models import RequestOptions
from .parameters import (
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
from .parsing import parse_obj_as, Parser
from .types import CookieTypes, HeaderTypes, PathParamTypes, QueryParamTypes

P = TypeVar("P", contravariant=True, bound=param.parameters.Param)
PA = TypeVar("PA", contravariant=True, bound=Param)
PS = TypeVar("PS", contravariant=True, bound=Params)
T = TypeVar("T")


def noop_consumer(_: RequestOptions, /) -> None:
    pass


class Composer(Protocol[P]):
    def __call__(
        self,
        param: P,
        argument: Any,
        /,
    ) -> RequestConsumer:
        ...

C = TypeVar("C", bound=Composer)


@dataclass
class ParamComposer(Composer[PA]):
    consumer_factory: "RequestConsumerFactory[str, Any]"

    def __call__(
        self,
        param: PA,
        argument: Any,
        /,
    ) -> RequestConsumer:
        if param.alias is None:
            raise ResolutionError("Cannot compose `Param` with no alias")

        if argument is None and param.default is not Required:
            return noop_consumer

        return self.consumer_factory(param.alias, argument)

@dataclass
class ParamsComposer(Composer[PS], Generic[PS, T]):
    parser: Parser[T]
    consumer_factory: "RequestConsumerFactory[T]"

    def __call__(
        self,
        _: PS,
        argument: Any,
        /,
    ) -> RequestConsumer:
        parsed: T = self.parser(argument)

        return self.consumer_factory(parsed)


class Composers(Register[Type[param.parameters.Param], C]):
    pass


compose_query_param: Composer = ParamComposer(QueryParamConsumer.parse)
compose_header: Composer = ParamComposer(HeaderConsumer.parse)
compose_cookie: Composer = ParamComposer(CookieConsumer.parse)
compose_path_param: Composer = ParamComposer(PathParamConsumer.parse)

compose_query_params: Composer = ParamsComposer(
    parser=Parser(QueryParamTypes),
    consumer_factory=QueryParamsConsumer.parse,
)
compose_headers: Composer = ParamsComposer(
    parser=Parser(HeaderTypes),
    consumer_factory=HeadersConsumer.parse,
)
compose_cookies: Composer = ParamsComposer(
    parser=Parser(CookieTypes),
    consumer_factory=CookiesConsumer.parse,
)
compose_path_params: Composer = ParamsComposer(
    parser=Parser(PathParamTypes),
    consumer_factory=PathParamsConsumer.parse,
)

composers: Composers[Composer] = Composers(
    {
        Query: compose_query_param,
        Header: compose_header,
        Cookie: compose_cookie,
        Path: compose_path_param,

        QueryParams: compose_query_params,
        Headers: compose_headers,
        Cookies: compose_cookies,
        PathParams: compose_path_params,
    }
)


# @composers(QueryParams)
# def compose_query_params(
#     _: QueryParams,
#     argument: Any,
# ) -> RequestConsumer:
#     parser: Parser[QueryParamTypes] = Parser(QueryParamTypes)

#     query_params: QueryParamTypes = parser(argument)

#     return QueryParamsConsumer.parse(query_params)


# @composers(Headers)
# def compose_headers(
#     _: Headers,
#     argument: Any,
# ) -> RequestConsumer:
#     parser: Parser[HeaderTypes] = Parser(HeaderTypes)
    
#     headers: HeaderTypes = parser(argument)

#     return HeadersConsumer.parse(headers)


# @composers(Cookies)
# def compose_cookies(
#     _: Cookies,
#     argument: Any,
# ) -> RequestConsumer:
#     parser: Parser[CookieTypes] = Parser(CookieTypes)
    
#     cookies: CookieTypes = parser(argument)

#     return CookiesConsumer.parse(cookies)


# @composers(PathParams)
# def compose_path_params(
#     _: PathParams,
#     argument: Any,
# ) -> RequestConsumer:
#     parser: Parser[PathParamTypes] = Parser(PathParamTypes)
    
#     path_params: PathParamTypes = parser(argument)

#     return PathParamsConsumer.parse(path_params)


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
        raise ResolutionError(f"Failed to find composer for param {param!r}")

    logger.info(f"Found composer: {composer!r}")

    consumer: RequestConsumer = composer(param, argument)

    logger.info(f"Applying request consumer: {consumer!r}")

    consumer(request)
