from typing import Any, Optional, Protocol, Type, TypeVar

import param
import param.parameters
from loguru import logger
from param.errors import ResolutionError
from pydantic import Required
from mediate import middleware
from roster import Register

from .composition import wrappers
from .composition.typing import RequestConsumer
from .models import RequestOptions
from .parameters import (
    Cookie,
    Cookies,
    Header,
    Headers,
    Param,
    Path,
    PathParams,
    Query,
    QueryParams,
)
from .parsing import parse_obj_as
from .types import CookieTypes, HeaderTypes, PathParamTypes, QueryParamTypes

P = TypeVar("P", contravariant=True, bound=param.parameters.Param)
PA = TypeVar("PA", contravariant=True, bound=Param)


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


class Composers(Register[Type[param.parameters.Param], C]):
    pass


composers: Composers[Composer] = Composers()


def requires_alias(
    call_next: Composer[Param], param: Param, argument: Any
) -> RequestConsumer:
    if param.alias is None:
        raise ResolutionError("Cannot compose `Param` with no alias")

    return call_next(param, argument)


def ignorable(
    call_next: Composer[Param], param: Param, argument: Any
) -> RequestConsumer:
    if argument is None and param.default is not Required:
        return noop_consumer

    return call_next(param, argument)


@composers(Query)
@middleware(requires_alias, ignorable)
def compose_query_param(
    param: Param,
    argument: Any,
) -> RequestConsumer:
    return wrappers.query(param.alias, argument)


@composers(Header)
@middleware(requires_alias, ignorable)
def compose_header(
    param: Param,
    argument: Any,
) -> RequestConsumer:
    return wrappers.header(param.alias, argument)


@composers(Cookie)
@middleware(requires_alias, ignorable)
def compose_cookie(
    param: Param,
    argument: Any,
) -> RequestConsumer:
    return wrappers.cookie(param.alias, argument)


@composers(Path)
@middleware(requires_alias, ignorable)
def compose_path_param(
    param: Param,
    argument: Any,
) -> RequestConsumer:
    return wrappers.path(param.alias, argument)


@composers(QueryParams)
def compose_query_params(
    _: QueryParams,
    argument: Any,
) -> RequestConsumer:
    query_params: QueryParamTypes = parse_obj_as(QueryParamTypes, argument)

    return wrappers.query_params(query_params)


@composers(Headers)
def compose_headers(
    _: Headers,
    argument: Any,
) -> RequestConsumer:
    headers: HeaderTypes = parse_obj_as(HeaderTypes, argument)

    return wrappers.headers(headers)


@composers(Cookies)
def compose_cookies(
    _: Cookies,
    argument: Any,
) -> RequestConsumer:
    cookies: CookieTypes = parse_obj_as(CookieTypes, argument)

    return wrappers.cookies(cookies)


@composers(PathParams)
def compose_path_params(
    _: PathParams,
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
