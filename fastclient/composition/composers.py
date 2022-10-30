from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, Protocol, Type, TypeVar

import fastapi.encoders
import param
import param.parameters
from param.errors import ResolutionError
from pydantic import Required
from roster import Register

from fastclient.models import RequestOptions

from ..parameters import (
    BodyParameter,
    CookieParameter,
    CookiesParameter,
    HeaderParameter,
    HeadersParameter,
    PathParameter,
    PathsParameter,
    QueriesParameter,
    QueryParameter,
    _BaseMultiParameter,
    _BaseSingleParameter,
)
from ..parsing import Parser
from ..types import CookieTypes, HeaderTypes, PathParamTypes, QueryParamTypes
from ..utils import noop_consumer
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
from .typing import RequestConsumer

P = TypeVar("P", contravariant=True, bound=param.parameters.Param)
PA = TypeVar("PA", contravariant=True, bound=_BaseSingleParameter)
PS = TypeVar("PS", contravariant=True, bound=_BaseMultiParameter)
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
class QueryParamComposer(ParamComposer[QueryParameter]):
    @staticmethod
    def build_consumer(key: str, value: Any) -> RequestConsumer:
        return QueryParamConsumer.parse(key, value)


@dataclass
class HeaderComposer(ParamComposer[QueryParameter]):
    @staticmethod
    def build_consumer(key: str, value: Any) -> RequestConsumer:
        return HeaderConsumer.parse(key, value)


@dataclass
class CookieComposer(ParamComposer[QueryParameter]):
    @staticmethod
    def build_consumer(key: str, value: Any) -> RequestConsumer:
        return CookieConsumer.parse(key, value)


@dataclass
class PathParamComposer(ParamComposer[QueryParameter]):
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
class QueryParamsComposer(ParamsComposer[QueriesParameter, QueryParamTypes]):
    @staticmethod
    def build_consumer(params: QueryParamTypes, /) -> RequestConsumer:
        return QueryParamsConsumer.parse(params)

    @staticmethod
    def parse(value: Any, /) -> QueryParamTypes:
        return Parser(QueryParamTypes)(value)


@dataclass
class HeadersComposer(ParamsComposer[HeadersParameter, HeaderTypes]):
    @staticmethod
    def build_consumer(headers: HeaderTypes, /) -> RequestConsumer:
        return HeadersConsumer.parse(headers)

    @staticmethod
    def parse(value: Any, /) -> HeaderTypes:
        return Parser(HeaderTypes)(value)


@dataclass
class CookiesComposer(ParamsComposer[CookiesParameter, CookieTypes]):
    @staticmethod
    def build_consumer(cookies: CookieTypes, /) -> RequestConsumer:
        return CookiesConsumer.parse(cookies)

    @staticmethod
    def parse(value: Any, /) -> CookieTypes:
        return Parser(CookieTypes)(value)


@dataclass
class PathParamsComposer(ParamsComposer[PathsParameter, PathParamTypes]):
    @staticmethod
    def build_consumer(path_params: PathParamTypes, /) -> RequestConsumer:
        return PathParamsConsumer.parse(path_params)

    @staticmethod
    def parse(value: Any, /) -> PathParamTypes:
        return Parser(PathParamTypes)(value)


# NOTE: This resolver is currently untested
# TODO: Add some middleware that sets/unsets `embed` as appropriate
def compose_body(
    param: BodyParameter,
    argument: Any,
) -> RequestConsumer:
    # If the param is not required and has no value, it can be omitted
    if argument is None and param.default is not Required:
        return noop_consumer

    json_value: Any = fastapi.encoders.jsonable_encoder(argument)

    if param.embed:
        if param.alias is None:
            raise ResolutionError("Cannot embed `Body` with no alias")

        json_value = {param.alias: json_value}

    # If this param shouln't be embedded in any pre-existing json,
    # make it the entire JSON request body
    if not param.embed:

        def consume(request: RequestOptions, /) -> None:
            request.json = json_value

        return consume
    else:

        def consume(request: RequestOptions, /) -> None:
            if request.json is None:
                request.json = json_value
            else:
                request.json.update(json_value)

        return consume


class Composers(Register[Type[param.parameters.Param], C]):
    pass


composers: Composers[Composer] = Composers(
    {
        QueryParameter: QueryParamComposer(),
        HeaderParameter: HeaderComposer(),
        CookieParameter: CookieComposer(),
        PathParameter: PathParamComposer(),
        QueriesParameter: QueryParamsComposer(),
        HeadersParameter: HeadersComposer(),
        CookiesParameter: CookiesComposer(),
        PathsParameter: PathParamsComposer(),
        BodyParameter: compose_body,
    }
)
