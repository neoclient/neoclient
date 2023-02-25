from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Generic, Mapping, Optional, Sequence, Set, TypeVar, Union

import fastapi.encoders
import httpx
from httpx import Cookies, Headers, QueryParams
from pydantic import Required
from pydantic.fields import FieldInfo, ModelField

from .consumers import (
    CookieConsumer,
    CookiesConsumer,
    HeaderConsumer,
    HeadersConsumer,
    PathConsumer,
    PathsConsumer,
    StateConsumer,
    QueriesConsumer,
    QueryConsumer,
)
from .converters import (
    convert_cookie,
    convert_header,
    convert_path_param,
    convert_query_param,
)
from .errors import CompositionError, ResolutionError
from .models import RequestOptions
from .resolvers import (
    BodyResolver,
    CookieResolver,
    CookiesResolver,
    HeaderResolver,
    HeadersResolver,
    QueriesResolver,
    QueryResolver,
)
from .types import CookiesTypes, HeadersTypes, PathsTypes, QueriesTypes
from .typing import RequestConsumer, Resolver, Supplier
from .utils import parse_obj_as

__all__: Sequence[str] = (
    "QueryParameter",
    "HeaderParameter",
    "CookieParameter",
    "PathParameter",
    "QueriesParameter",
    "HeadersParameter",
    "CookiesParameter",
    "PathsParameter",
    "BodyParameter",
    "URLParameter",
    "ResponseParameter",
    "RequestParameter",
    "StatusCodeParameter",
)

K = TypeVar("K")
V = TypeVar("V")


@dataclass(unsafe_hash=True)
class Parameter(FieldInfo):
    alias: Optional[str] = None
    default: Any = Required
    default_factory: Optional[Supplier[Any]] = None
    title: Optional[str] = field(default=None, compare=False)
    description: Optional[str] = field(default=None, compare=False)
    exclude: Union[Set[Union[int, str]], Mapping[Union[int, str], Any], Any] = field(
        default=None, compare=False
    )
    include: Union[Set[Union[int, str]], Mapping[Union[int, str], Any], Any] = field(
        default=None, compare=False
    )
    const: Optional[bool] = field(default=None, compare=False)
    gt: Optional[float] = field(default=None, compare=False)
    ge: Optional[float] = field(default=None, compare=False)
    lt: Optional[float] = field(default=None, compare=False)
    le: Optional[float] = field(default=None, compare=False)
    multiple_of: Optional[float] = field(default=None, compare=False)
    allow_inf_nan: Optional[bool] = field(default=None, compare=False)
    max_digits: Optional[int] = field(default=None, compare=False)
    decimal_places: Optional[int] = field(default=None, compare=False)
    min_items: Optional[int] = field(default=None, compare=False)
    max_items: Optional[int] = field(default=None, compare=False)
    unique_items: Optional[bool] = field(default=None, compare=False)
    min_length: Optional[int] = field(default=None, compare=False)
    max_length: Optional[int] = field(default=None, compare=False)
    allow_mutation: bool = field(default=True, compare=False)
    regex: Optional[str] = field(default=None, compare=False)
    discriminator: Optional[str] = field(default=None, compare=False)
    repr: bool = field(default=True, compare=False)
    extra: Dict[str, Any] = field(default_factory=dict, compare=False)
    alias_priority: Optional[int] = field(
        init=False, repr=False, default=None, compare=False
    )

    def __post_init__(self) -> None:
        # Pydantic validates that the alias is a "strict" string. This means
        # that enums (e.g. `HeaderName`) are unable to be used.
        # To mitigate this, the alias is explicity converted to a string here.
        if self.alias is not None:
            self.alias = str(self.alias)

    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        raise CompositionError(f"Parameter {type(self)!r} is not composable")

    def resolve(self, response: httpx.Response, /) -> Any:
        raise ResolutionError(f"Parameter {type(self)!r} is not resolvable")

    def prepare(self, model_field: ModelField, /) -> None:
        if self.alias is None:
            self.alias = model_field.name


class ComposableSingletonParameter(ABC, Parameter, Generic[K, V]):
    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        if self.alias is None:
            raise CompositionError(
                f"Cannot compose parameter {type(self)!r} without an alias"
            )

        if argument is None and self.default is not Required:
            return

        consumer: RequestConsumer = self.build_consumer(
            self.parse_key(self.alias),
            self.parse_value(argument),
        )

        consumer(request)

    @abstractmethod
    def parse_key(self, key: str, /) -> K:
        ...

    @abstractmethod
    def parse_value(self, value: Any, /) -> V:
        ...

    @abstractmethod
    def build_consumer(self, key: K, value: V) -> RequestConsumer:
        ...


class ResolvableSingletonParameter(ABC, Parameter, Generic[K, V]):
    def resolve(self, response: httpx.Response, /) -> V:
        if self.alias is None:
            raise ResolutionError(
                f"Cannot resolve parameter {type(self)!r} without an alias"
            )

        resolver: Resolver[V] = self.build_resolver(
            self.parse_key(self.alias),
        )

        return resolver(response)

    @abstractmethod
    def parse_key(self, key: str, /) -> K:
        ...

    @abstractmethod
    def build_resolver(self, key: K) -> Resolver[V]:
        ...


class ComposableSingletonStringParameter(ComposableSingletonParameter[str, str]):
    def parse_key(self, key: str, /) -> str:
        return key


class ResolvableSingletonStringParameter(
    ResolvableSingletonParameter[str, Optional[str]]
):
    def parse_key(self, key: str, /) -> str:
        return key


class QueryParameter(
    ComposableSingletonStringParameter, ResolvableSingletonStringParameter
):
    def parse_value(self, value: Any, /) -> str:
        return convert_query_param(value)

    def build_consumer(self, key: str, value: str) -> RequestConsumer:
        return QueryConsumer(key, value)

    def build_resolver(self, key: str) -> Resolver[Optional[str]]:
        return QueryResolver(key)


@dataclass(unsafe_hash=True)
class HeaderParameter(
    ComposableSingletonStringParameter, ResolvableSingletonStringParameter
):
    convert_underscores: bool = True

    def parse_key(self, key: str, /) -> str:
        if self.convert_underscores:
            return key.replace("_", "-")
        else:
            return key

    def parse_value(self, value: Any, /) -> str:
        return convert_header(value)

    def build_consumer(self, key: str, value: str) -> RequestConsumer:
        return HeaderConsumer(key, value)

    def build_resolver(self, key: str) -> Resolver[Optional[str]]:
        return HeaderResolver(key)


class CookieParameter(
    ComposableSingletonStringParameter, ResolvableSingletonStringParameter
):
    def parse_value(self, value: Any, /) -> str:
        return convert_cookie(value)

    def build_consumer(self, key: str, value: str) -> RequestConsumer:
        return CookieConsumer(key, value)

    def build_resolver(self, key: str) -> Resolver[Optional[str]]:
        return CookieResolver(key)


class PathParameter(ComposableSingletonStringParameter):
    def parse_value(self, value: Any, /) -> str:
        return convert_path_param(value)

    def build_consumer(self, key: str, value: str) -> RequestConsumer:
        return PathConsumer(key, value)


class QueriesParameter(Parameter):
    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        params: QueriesTypes = parse_obj_as(QueriesTypes, argument)  # type: ignore

        QueriesConsumer(params)(request)

    def resolve(self, response: httpx.Response, /) -> QueryParams:
        return QueriesResolver()(response)


class HeadersParameter(Parameter):
    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        headers: HeadersTypes = parse_obj_as(HeadersTypes, argument)  # type: ignore

        HeadersConsumer(headers)(request)

    def resolve(self, response: httpx.Response, /) -> Headers:
        return HeadersResolver()(response)


class CookiesParameter(Parameter):
    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        cookies: CookiesTypes = parse_obj_as(CookiesTypes, argument)  # type: ignore

        CookiesConsumer(cookies)(request)

    def resolve(self, response: httpx.Response, /) -> Cookies:
        return CookiesResolver()(response)


class PathsParameter(Parameter):
    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        path_params: PathsTypes = parse_obj_as(PathsTypes, argument)  # type: ignore

        PathsConsumer(path_params)(request)


@dataclass(unsafe_hash=True)
class BodyParameter(Parameter):
    embed: bool = False

    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        # If the parameter is not required and has no value, it can be omitted
        if argument is None and self.default is not Required:
            return

        json_value: Any = fastapi.encoders.jsonable_encoder(argument)

        if self.embed:
            if self.alias is None:
                raise CompositionError(
                    f"Cannot embed parameter {type(self)!r} without an alias"
                )

            json_value = {self.alias: json_value}

        # If this parameter shouln't be embedded in any pre-existing json,
        # make it the entire JSON request body
        if not self.embed:
            request.json = json_value
        else:
            if request.json is None:
                request.json = json_value
            else:
                request.json.update(json_value)

    def resolve(self, response: httpx.Response, /) -> Any:
        return BodyResolver()(response)


class URLParameter(Parameter):
    def resolve(self, response: httpx.Response, /) -> httpx.URL:
        return response.request.url


class ResponseParameter(Parameter):
    def resolve(self, response: httpx.Response, /) -> httpx.Response:
        return response


class RequestParameter(Parameter):
    def resolve(self, response: httpx.Response, /) -> httpx.Request:
        return response.request


class StatusCodeParameter(Parameter):
    def resolve(self, response: httpx.Response, /) -> int:
        return response.status_code


class StateParameter(ComposableSingletonParameter[str, Any]):
    def parse_key(self, key: str, /) -> str:
        return key

    def parse_value(self, value: Any, /) -> Any:
        return value

    def build_consumer(self, key: str, value: Any) -> RequestConsumer:
        return StateConsumer(key, value)
