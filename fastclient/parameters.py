from dataclasses import dataclass, field
from typing import Any, Dict, Generic, List, Mapping, Optional, Set, TypeVar, Union

import fastapi.encoders
import httpx
from httpx import Cookies, Headers, QueryParams
from pydantic import Required
from pydantic.fields import FieldInfo, ModelField, Undefined, UndefinedType

from .composition.consumers import (
    CookieConsumer,
    CookiesConsumer,
    HeaderConsumer,
    HeadersConsumer,
    PathConsumer,
    PathsConsumer,
    QueriesConsumer,
    QueryConsumer,
)
from .errors import CompositionError, ResolutionError
from .models import RequestOptions
from .parsing import parse_obj_as
from .resolution.functions import (
    BodyResolutionFunction,
    CookieResolutionFunction,
    CookiesResolutionFunction,
    HeaderResolutionFunction,
    HeadersResolutionFunction,
    QueriesResolutionFunction,
    QueryResolutionFunction,
)
from .types import CookiesTypes, HeadersTypes, PathsTypes, QueriesTypes
from .typing import Supplier

__all__: List[str] = [
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
]

T = TypeVar("T")


@dataclass
class BaseParameter(FieldInfo):
    default: Union[Any, UndefinedType] = Undefined
    default_factory: Optional[Supplier[Any]] = None
    alias: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    exclude: Union[Set[Union[int, str]], Mapping[Union[int, str], Any], Any] = None
    include: Union[Set[Union[int, str]], Mapping[Union[int, str], Any], Any] = None
    const: Optional[bool] = None
    gt: Optional[float] = None
    ge: Optional[float] = None
    lt: Optional[float] = None
    le: Optional[float] = None
    multiple_of: Optional[float] = None
    allow_inf_nan: Optional[bool] = None
    max_digits: Optional[int] = None
    decimal_places: Optional[int] = None
    min_items: Optional[int] = None
    max_items: Optional[int] = None
    unique_items: Optional[bool] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allow_mutation: bool = True
    regex: Optional[str] = None
    discriminator: Optional[str] = None
    repr: bool = True
    extra: Dict[str, Any] = field(default_factory=dict)
    alias_priority: Optional[int] = field(init=False, repr=False, default=None)

    @staticmethod
    def generate_alias(alias: str, /) -> str:
        return alias

    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        raise CompositionError(f"Parameter {type(self)!r} is not composable")

    def resolve(self, response: httpx.Response, /) -> Any:
        raise ResolutionError(f"Parameter {type(self)!r} is not resolvable")

    def prepare(self, field: ModelField, /) -> None:
        # NOTE: Ideally these `.prepare` calls wouldn't modify the existing parameter and would
        # instead return a modified copy.
        if self.alias is None:
            self.alias = self.generate_alias(field.name)


class BaseSingleParameter(BaseParameter):
    @staticmethod
    def generate_alias(alias: str):
        return alias


class BaseMultiParameter(BaseParameter, Generic[T]):
    pass


class QueryParameter(BaseSingleParameter):
    @staticmethod
    def generate_alias(alias: str):
        return alias.lower().replace("_", "-")

    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        if self.alias is None:
            raise CompositionError(
                f"Cannot compose parameter {type(self)!r} without an alias"
            )

        if argument is None and self.default is not Required:
            return

        QueryConsumer.parse(self.alias, argument)(request)

    def resolve(self, response: httpx.Response, /) -> Optional[str]:
        if self.alias is None:
            raise ResolutionError(
                f"Cannot resolve parameter {type(self)!r} without an alias"
            )

        return QueryResolutionFunction(self.alias)(response)


class HeaderParameter(BaseSingleParameter):
    @staticmethod
    def generate_alias(alias: str):
        return alias.title().replace("_", "-")

    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        if self.alias is None:
            raise CompositionError(
                f"Cannot compose parameter {type(self)!r} without an alias"
            )

        if argument is None and self.default is not Required:
            return

        HeaderConsumer.parse(self.alias, argument)(request)

    def resolve(self, response: httpx.Response, /) -> Optional[str]:
        if self.alias is None:
            raise ResolutionError(
                f"Cannot resolve parameter {type(self)!r} without an alias"
            )

        return HeaderResolutionFunction(self.alias)(response)


class CookieParameter(BaseSingleParameter):
    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        if self.alias is None:
            raise CompositionError(
                f"Cannot compose parameter {type(self)!r} without an alias"
            )

        if argument is None and self.default is not Required:
            return

        CookieConsumer.parse(self.alias, argument)(request)

    def resolve(self, response: httpx.Response, /) -> Optional[str]:
        if self.alias is None:
            raise ResolutionError(
                f"Cannot resolve parameter {type(self)!r} without an alias"
            )

        return CookieResolutionFunction(self.alias)(response)


class PathParameter(BaseSingleParameter):
    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        if self.alias is None:
            raise CompositionError(
                f"Cannot compose parameter {type(self)!r} without an alias"
            )

        if argument is None and self.default is not Required:
            return

        PathConsumer.parse(self.alias, argument)(request)


class QueriesParameter(BaseMultiParameter[QueriesTypes]):
    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        params: QueriesTypes = parse_obj_as(QueriesTypes, argument)  # type: ignore

        QueriesConsumer.parse(params)(request)

    def resolve(self, response: httpx.Response, /) -> QueryParams:
        return QueriesResolutionFunction()(response)


class HeadersParameter(BaseMultiParameter[HeadersTypes]):
    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        headers: HeadersTypes = parse_obj_as(HeadersTypes, argument)  # type: ignore

        HeadersConsumer.parse(headers)(request)

    def resolve(self, response: httpx.Response, /) -> Headers:
        return HeadersResolutionFunction()(response)


class CookiesParameter(BaseMultiParameter[CookiesTypes]):
    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        cookies: CookiesTypes = parse_obj_as(CookiesTypes, argument)  # type: ignore

        CookiesConsumer.parse(cookies)(request)

    def resolve(self, response: httpx.Response, /) -> Cookies:
        return CookiesResolutionFunction()(response)


class PathsParameter(BaseMultiParameter[PathsTypes]):
    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        path_params: PathsTypes = parse_obj_as(PathsTypes, argument)  # type: ignore

        PathsConsumer.parse(path_params)(request)


@dataclass
class BodyParameter(BaseParameter):
    embed: bool = False

    @staticmethod
    def generate_alias(alias: str):
        return alias

    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        # If the parameter is not required and has no value, it can be omitted
        # NOTE: This functionality is shared with the "single" parameters (e.g. Query, Header, ...)
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
        return BodyResolutionFunction()(response)


@dataclass
class URLParameter(BaseParameter):
    def resolve(self, response: httpx.Response, /) -> httpx.URL:
        return response.request.url


@dataclass
class ResponseParameter(BaseParameter):
    def resolve(self, response: httpx.Response, /) -> httpx.Response:
        return response


@dataclass
class RequestParameter(BaseParameter):
    def resolve(self, response: httpx.Response, /) -> httpx.Request:
        return response.request


@dataclass
class StatusCodeParameter(BaseParameter):
    def resolve(self, response: httpx.Response, /) -> int:
        return response.status_code
