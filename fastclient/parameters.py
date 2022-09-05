from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    Optional,
    Type,
    TypeVar,
    Union,
)

from httpx import Request, Response
import param.models
from param.sentinels import Missing, MissingType

from .enums import ParamType

T = TypeVar("T")


@dataclass(frozen=True)
class Param(param.models.Param[T]):
    type: ClassVar[ParamType]

    alias: Optional[str] = None
    required: bool = False

    @staticmethod
    def generate_alias(alias: str):
        return alias


class Path(Param[T]):
    type: ClassVar[ParamType] = ParamType.PATH

    @staticmethod
    def generate_alias(alias: str):
        return alias.lower().replace("_", "-")


class Query(Param[T]):
    type: ClassVar[ParamType] = ParamType.QUERY

    @staticmethod
    def generate_alias(alias: str):
        return alias.lower().replace("_", "-")


class Header(Param[T]):
    type: ClassVar[ParamType] = ParamType.HEADER

    @staticmethod
    def generate_alias(alias: str):
        return alias.title().replace("_", "-")


class Cookie(Param[T]):
    type: ClassVar[ParamType] = ParamType.COOKIE

    @staticmethod
    def generate_alias(alias: str):
        return alias.upper()


@dataclass(frozen=True)
class Body(Param[T]):
    type: ClassVar[ParamType] = ParamType.BODY

    embed: bool = False


# NOTE: Should use custom generic types for each subclass. E.g. `Headers` should have a `T` bound to `HeaderTypes`
class Params(param.models.Param[Dict[str, Any]]):
    type: ClassVar[ParamType]

    def __init__(
        self,
        *,
        default_factory: Union[Callable[[], Dict[str, Any]], MissingType] = Missing,
    ):
        super().__init__(
            default_factory=default_factory if default_factory is not Missing else dict
        )


class QueryParams(Params):
    type: ClassVar[ParamType] = ParamType.QUERY


class Headers(Params):
    type: ClassVar[ParamType] = ParamType.HEADER


class Cookies(Params):
    type: ClassVar[ParamType] = ParamType.COOKIE


class PathParams(Params):
    type: ClassVar[ParamType] = ParamType.PATH


# NOTE: Don't use @dataclass, this way can make `use_cache` keyword-only? (FastAPI does it this way)
@dataclass(frozen=True)
class Depends(param.models.ParameterSpecification, Generic[T]):
    dependency: Optional[Callable[..., T]] = None
    use_cache: bool = True


@dataclass(frozen=True)
class Promise(param.models.ParameterSpecification):
    promised_type: Union[None, Type[Request], Type[Response]] = None
