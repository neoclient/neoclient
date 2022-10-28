from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, Optional, Protocol, Type, TypeVar

import param
import param.parameters
from loguru import logger
from param.errors import ResolutionError
from pydantic import Required
from roster import Register

from .consumers import (
    CookieConsumer,
    CookiesConsumer,
    HeaderConsumer,
    HeadersConsumer,
    PathParamConsumer,
    PathParamsConsumer,
    QueryParamConsumer,
    QueryParamsConsumer,
)
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
from .parsing import Parser
from .types import CookieTypes, HeaderTypes, PathParamTypes, QueryParamTypes
from .typing import RequestConsumer
from .utils import noop_consumer

P = TypeVar("P", contravariant=True, bound=param.parameters.Param)
PA = TypeVar("PA", contravariant=True, bound=Param)
PS = TypeVar("PS", contravariant=True, bound=Params)
T = TypeVar("T")


class Composer(Protocol[P]):
    def __call__(
        self,
        param: P,
        argument: Any,
        /,
    ) -> RequestConsumer:
        ...


C = TypeVar("C", bound=Composer)


class ParamComposer(ABC, Composer[PA]):
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

        return self.build_consumer(param.alias, argument)

    @staticmethod
    @abstractmethod
    def build_consumer(key: str, value: Any) -> RequestConsumer:
        ...


@dataclass
class QueryParamComposer(ParamComposer[Query]):
    @staticmethod
    def build_consumer(key: str, value: Any) -> RequestConsumer:
        return QueryParamConsumer.parse(key, value)


@dataclass
class HeaderComposer(ParamComposer[Query]):
    @staticmethod
    def build_consumer(key: str, value: Any) -> RequestConsumer:
        return HeaderConsumer.parse(key, value)


@dataclass
class CookieComposer(ParamComposer[Query]):
    @staticmethod
    def build_consumer(key: str, value: Any) -> RequestConsumer:
        return CookieConsumer.parse(key, value)


@dataclass
class PathParamComposer(ParamComposer[Query]):
    @staticmethod
    def build_consumer(key: str, value: Any) -> RequestConsumer:
        return PathParamConsumer.parse(key, value)


class ParamsComposer(Composer[PS], Generic[PS, T]):
    def __call__(
        self,
        _: PS,
        argument: Any,
        /,
    ) -> RequestConsumer:
        parsed: T = self.parse(argument)

        return self.build_consumer(parsed)

    @staticmethod
    @abstractmethod
    def build_consumer(value: T, /) -> RequestConsumer:
        ...

    @staticmethod
    @abstractmethod
    def parse(value: Any, /) -> T:
        ...


@dataclass
class QueryParamsComposer(ParamsComposer[QueryParams, QueryParamTypes]):
    @staticmethod
    def build_consumer(params: QueryParamTypes, /) -> RequestConsumer:
        return QueryParamsConsumer.parse(params)

    @staticmethod
    def parse(value: Any, /) -> QueryParamTypes:
        return Parser(QueryParamTypes)(value)


@dataclass
class HeadersComposer(ParamsComposer[Headers, HeaderTypes]):
    @staticmethod
    def build_consumer(headers: HeaderTypes, /) -> RequestConsumer:
        return HeadersConsumer.parse(headers)

    @staticmethod
    def parse(value: Any, /) -> HeaderTypes:
        return Parser(HeaderTypes)(value)


@dataclass
class CookiesComposer(ParamsComposer[Cookies, CookieTypes]):
    @staticmethod
    def build_consumer(cookies: CookieTypes, /) -> RequestConsumer:
        return CookiesConsumer.parse(cookies)

    @staticmethod
    def parse(value: Any, /) -> CookieTypes:
        return Parser(CookieTypes)(value)


@dataclass
class PathParamsComposer(ParamsComposer[PathParams, PathParamTypes]):
    @staticmethod
    def build_consumer(path_params: PathParamTypes, /) -> RequestConsumer:
        return PathParamsConsumer.parse(path_params)

    @staticmethod
    def parse(value: Any, /) -> PathParamTypes:
        return Parser(PathParamTypes)(value)


class Composers(Register[Type[param.parameters.Param], C]):
    pass


composers: Composers[Composer] = Composers(
    {
        Query: QueryParamComposer(),
        Header: HeaderComposer(),
        Cookie: CookieComposer(),
        Path: PathParamComposer(),
        QueryParams: QueryParamsComposer(),
        Headers: HeadersComposer(),
        Cookies: CookiesComposer(),
        PathParams: PathParamsComposer(),
    }
)


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
