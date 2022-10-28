from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Generic, Optional, Protocol, Type, TypeVar
from typing_extensions import ParamSpec

import param
import param.parameters
from loguru import logger
from param.errors import ResolutionError
from pydantic import Required
from roster import Register

from . import converters
from .composition.consumers import (
    QueryParamConsumer,
    HeaderConsumer,
    CookieConsumer,
    PathParamConsumer,
    QueryParamsConsumer,
    HeadersConsumer,
    CookiesConsumer,
    PathParamsConsumer,
)
from .composition.typing import RequestConsumer, RequestConsumerFactory
# from .composition.models import Entry
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
from .parsing import parse_obj_as
from .types import CookieTypes, HeaderTypes, PathParamTypes, QueryParamTypes

P = TypeVar("P", contravariant=True, bound=param.parameters.Param)
PA = TypeVar("PA", contravariant=True, bound=Param)
PS = TypeVar("PS", contravariant=True, bound=Params)

BT = TypeVar("BT")
IT = TypeVar("IT")

# PS = ParamSpec("PS")


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

    # @staticmethod
    # @abstractmethod
    # def convert_value(value: Any, /) -> str:
    #     ...

    # @classmethod
    # @abstractmethod
    # def build_consumer(cls, key: str, value: Any) -> RequestConsumer:
    #     ...

# class ParamsComposer(Composer[PS], Generic[PS, IT]):
#     consumer_factory: "RequestConsumerFactory[IT]"

#     def __call__(
#         self,
#         param: PS,
#         argument: Any,
#         /,
#     ) -> RequestConsumer:
        

# @dataclass
# class QueryParamComposer(ParamComposer[Query]):
#     @staticmethod
#     def convert_value(value: Any, /) -> str:
#         return converters.convert_query_param(value)

#     @classmethod
#     def build_consumer(cls, key: str, value: Any) -> RequestConsumer:
#         return QueryParamConsumerFactory(Entry(key, cls.convert_value(value)))


# class HeaderComposer(ParamComposer[Header]):
#     @staticmethod
#     def convert_value(value: Any, /) -> str:
#         return converters.convert_header(value)

#     @classmethod
#     def build_consumer(cls, key: str, value: Any) -> RequestConsumer:
#         return HeaderConsumerFactory(Entry(key, cls.convert_value(value)))


# class CookieComposer(ParamComposer[Cookie]):
#     @staticmethod
#     def convert_value(value: Any, /) -> str:
#         return converters.convert_cookie(value)

#     @classmethod
#     def build_consumer(cls, key: str, value: Any) -> RequestConsumer:
#         return CookieConsumerFactory(Entry(key, cls.convert_value(value)))


# class PathParamComposer(ParamComposer[Path]):
#     @staticmethod
#     def convert_value(value: Any, /) -> str:
#         return converters.convert_path_param(value)

#     @classmethod
#     def build_consumer(cls, key: str, value: Any) -> RequestConsumer:
#         return PathParamConsumerFactory(cls.bundle(key, value))


C = TypeVar("C", bound=Composer)


class Composers(Register[Type[param.parameters.Param], C]):
    pass


compose_query_param: Composer = ParamComposer(QueryParamConsumer.parse)
compose_header: Composer = ParamComposer(HeaderConsumer.parse)
compose_cookie: Composer = ParamComposer(CookieConsumer.parse)
compose_path_param: Composer = ParamComposer(PathParamConsumer.parse)

# compose_query_param: Composer = QueryParamComposer()
# compose_header: Composer = HeaderComposer()
# compose_cookie: Composer = CookieComposer()
# compose_path_param: Composer = PathParamComposer()

composers: Composers[Composer] = Composers(
    {
        Query: compose_query_param,
        Header: compose_header,
        Cookie: compose_cookie,
        Path: compose_path_param,
    }
)


@composers(QueryParams)
def compose_query_params(
    _: QueryParams,
    argument: Any,
) -> RequestConsumer:
    query_params: QueryParamTypes = parse_obj_as(QueryParamTypes, argument)

    return QueryParamsConsumer.parse(query_params)


@composers(Headers)
def compose_headers(
    _: Headers,
    argument: Any,
) -> RequestConsumer:
    headers: HeaderTypes = parse_obj_as(HeaderTypes, argument)

    return HeadersConsumer.parse(headers)


@composers(Cookies)
def compose_cookies(
    _: Cookies,
    argument: Any,
) -> RequestConsumer:
    cookies: CookieTypes = parse_obj_as(CookieTypes, argument)

    return CookiesConsumer.parse(cookies)


@composers(PathParams)
def compose_path_params(
    _: PathParams,
    argument: Any,
) -> RequestConsumer:
    path_params: PathParamTypes = parse_obj_as(PathParamTypes, argument)

    return PathParamsConsumer.parse(path_params)


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
