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

from httpx import Request, Response
from pydantic.fields import FieldInfo, Undefined, UndefinedType

from .enums import ParamType
from .types import CookieTypes, HeaderTypes, PathParamTypes, QueryParamTypes
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
    "DependencyParameter",
    "PromiseParameter",
]

T = TypeVar("T")


@dataclass(frozen=True)
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

    def __init__(
        self,
        *,
        default: Union[T, UndefinedType] = Undefined,
        default_factory: Optional[Supplier[T]] = None,
    ):
        super().__init__(
            default=default,
            default_factory=default_factory,
        )


class QueryParameter(BaseSingleParameter):
    type: ClassVar[ParamType] = ParamType.QUERY

    @staticmethod
    def generate_alias(alias: str):
        return alias.lower().replace("_", "-")


class HeaderParameter(BaseSingleParameter):
    type: ClassVar[ParamType] = ParamType.HEADER

    @staticmethod
    def generate_alias(alias: str):
        return alias.title().replace("_", "-")


class CookieParameter(BaseSingleParameter):
    type: ClassVar[ParamType] = ParamType.COOKIE


class PathParameter(BaseSingleParameter):
    type: ClassVar[ParamType] = ParamType.PATH


class QueriesParameter(BaseMultiParameter[QueryParamTypes]):
    type: ClassVar[ParamType] = ParamType.QUERY


class HeadersParameter(BaseMultiParameter[HeaderTypes]):
    type: ClassVar[ParamType] = ParamType.HEADER


class CookiesParameter(BaseMultiParameter[CookieTypes]):
    type: ClassVar[ParamType] = ParamType.COOKIE


class PathsParameter(BaseMultiParameter[PathParamTypes]):
    type: ClassVar[ParamType] = ParamType.PATH


@dataclass(frozen=True)
class BodyParameter(BaseParameter):
    embed: bool = False

    @staticmethod
    def generate_alias(alias: str):
        return alias


@dataclass(frozen=True, init=False)
class DependencyParameter(BaseParameter):
    dependency: Optional[Callable] = None
    use_cache: bool = True

    def __init__(
        self,
        dependency: Optional[Callable] = None,
        /,
        *,
        use_cache: bool = True,
    ):
        super().__init__()

        object.__setattr__(self, "dependency", dependency)
        object.__setattr__(self, "use_cache", use_cache)


@dataclass(frozen=True)
class PromiseParameter(BaseParameter):
    promised_type: Union[None, Type[Request], Type[Response]] = None
