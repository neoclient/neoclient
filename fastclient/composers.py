from dataclasses import dataclass
from typing import Any, Callable, Optional, Protocol, Type, TypeVar
from typing_extensions import ParamSpec

import param
import param.parameters
from loguru import logger
from param.errors import ResolutionError
from pydantic import Required
from roster import Register

from .composition import wrappers, bundlers
from .composition.factories import (
    QueryParamConsumerFactory,
    HeaderConsumerFactory,
    CookieConsumerFactory,
    PathParamConsumerFactory,
)
from .composition.typing import RequestConsumer, RequestConsumerFactory
from .composition.models import Entry
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

BT = TypeVar("BT")

PS = ParamSpec("PS")


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


@dataclass
class ParamComposer(Composer):
    request_consumer_factory: RequestConsumerFactory[Entry[str, str]]
    bundler: Callable[[str, Any], Entry[str, str]]

    def __call__(
        self,
        param: P,
        argument: Any,
        /,
    ) -> RequestConsumer:
        if param.alias is None:
            raise ResolutionError("Cannot compose `Param` with no alias")

        if argument is None and param.default is not Required:
            return noop_consumer

        bundled: Entry[str, str] = self.bundler(param.alias, argument)

        return self.request_consumer_factory(bundled)


C = TypeVar("C", bound=Composer)


class Composers(Register[Type[param.parameters.Param], C]):
    pass


composers: Composers[Composer] = Composers()

compose_query_param: Composer = ParamComposer(
    request_consumer_factory=QueryParamConsumerFactory,
    bundler=bundlers.query,
)
compose_header: Composer = ParamComposer(
    request_consumer_factory=HeaderConsumerFactory,
    bundler=bundlers.header,
)
compose_cookie: Composer = ParamComposer(
    request_consumer_factory=CookieConsumerFactory,
    bundler=bundlers.cookie,
)
compose_path_param: Composer = ParamComposer(
    request_consumer_factory=PathParamConsumerFactory,
    bundler=bundlers.path,
)

composers(Query)(compose_query_param)
composers(Header)(compose_header)
composers(Cookie)(compose_cookie)
composers(Path)(compose_path_param)


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
