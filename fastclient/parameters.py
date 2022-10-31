from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    List,
    Mapping,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
)

import fastapi.encoders
from httpx import Request, Response
from pydantic import Required
from pydantic.fields import FieldInfo, Undefined, UndefinedType

from .errors import CompositionError
from .enums import ParamType
from .models import RequestOptions
from .types import CookieTypes, HeaderTypes, PathParamTypes, QueryParamTypes
from .typing import Supplier
from .composition_consumers import (
    QueryConsumer,
    HeaderConsumer,
    CookieConsumer,
    PathConsumer,
    QueriesConsumer,
    HeadersConsumer,
    CookiesConsumer,
    PathsConsumer,
)
from .parsing import Parser

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
    "DependencyParameter",
    "PromiseParameter",
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

    def has_default(self) -> bool:
        return self.default is not Undefined or self.default_factory is not None

    def get_default(self) -> Any:
        if self.default_factory is not None:
            return self.default_factory()
        else:
            return self.default

    @staticmethod
    def generate_alias(alias: str, /) -> str:
        return alias


class BaseSingleParameter(BaseParameter):
    type: ClassVar[ParamType]

    @staticmethod
    def generate_alias(alias: str):
        return alias


class BaseMultiParameter(BaseParameter, Generic[T]):
    type: ClassVar[ParamType]


class QueryParameter(BaseSingleParameter):
    type: ClassVar[ParamType] = ParamType.QUERY

    @staticmethod
    def generate_alias(alias: str):
        return alias.lower().replace("_", "-")

    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        if self.alias is None:
            raise CompositionError(f"Cannot compose parameter {type(self)!r} without an alias")

        if argument is None and self.default is not Required:
            return

        QueryConsumer.parse(self.alias, argument)(request)


class HeaderParameter(BaseSingleParameter):
    type: ClassVar[ParamType] = ParamType.HEADER

    @staticmethod
    def generate_alias(alias: str):
        return alias.title().replace("_", "-")

    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        if self.alias is None:
            raise CompositionError(f"Cannot compose parameter {type(self)!r} without an alias")

        if argument is None and self.default is not Required:
            return

        HeaderConsumer.parse(self.alias, argument)(request)


class CookieParameter(BaseSingleParameter):
    type: ClassVar[ParamType] = ParamType.COOKIE

    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        if self.alias is None:
            raise CompositionError(f"Cannot compose parameter {type(self)!r} without an alias")

        if argument is None and self.default is not Required:
            return

        CookieConsumer.parse(self.alias, argument)(request)


class PathParameter(BaseSingleParameter):
    type: ClassVar[ParamType] = ParamType.PATH

    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        if self.alias is None:
            raise CompositionError(f"Cannot compose parameter {type(self)!r} without an alias")

        if argument is None and self.default is not Required:
            return

        PathConsumer.parse(self.alias, argument)(request)


class QueriesParameter(BaseMultiParameter[QueryParamTypes]):
    type: ClassVar[ParamType] = ParamType.QUERY

    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        params: QueryParamTypes = Parser(QueryParamTypes)(argument)

        QueriesConsumer.parse(params)(request)


class HeadersParameter(BaseMultiParameter[HeaderTypes]):
    type: ClassVar[ParamType] = ParamType.HEADER

    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        headers: HeaderTypes = Parser(HeaderTypes)(argument)

        HeadersConsumer.parse(headers)(request)


class CookiesParameter(BaseMultiParameter[CookieTypes]):
    type: ClassVar[ParamType] = ParamType.COOKIE

    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        cookies: CookieTypes = Parser(CookieTypes)(argument)

        CookiesConsumer.parse(cookies)(request)


class PathsParameter(BaseMultiParameter[PathParamTypes]):
    type: ClassVar[ParamType] = ParamType.PATH

    def compose(self, request: RequestOptions, argument: Any, /) -> None:
        path_params: PathParamTypes = Parser(PathParamTypes)(argument)

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
                raise CompositionError(f"Cannot embed parameter {type(self)!r} without an alias")

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


@dataclass
class DependencyParameter(BaseParameter):
    dependency: Optional[Callable] = None
    use_cache: bool = True


@dataclass
class PromiseParameter(BaseParameter):
    promised_type: Union[None, Type[Request], Type[Response]] = None
