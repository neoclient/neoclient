from dataclasses import dataclass
from typing import Callable, ClassVar, Generic, Optional, Type, Union, TypeVar

import param.parameters
from httpx import Request, Response
from param.typing import Supplier
from pydantic.fields import Undefined, UndefinedType

from .enums import ParamType
from .types import (
    QueryParamTypes,
    HeaderTypes,
    CookieTypes,
    PathParamTypes,
)

T = TypeVar("T")


class _BaseSingleParameter(param.parameters.Param):
    type: ClassVar[ParamType]

    @staticmethod
    def generate_alias(alias: str):
        return alias


class QueryParameter(_BaseSingleParameter):
    type: ClassVar[ParamType] = ParamType.QUERY

    @staticmethod
    def generate_alias(alias: str):
        return alias.lower().replace("_", "-")


class HeaderParameter(_BaseSingleParameter):
    type: ClassVar[ParamType] = ParamType.HEADER

    @staticmethod
    def generate_alias(alias: str):
        return alias.title().replace("_", "-")


class CookieParameter(_BaseSingleParameter):
    type: ClassVar[ParamType] = ParamType.COOKIE


class PathParameter(_BaseSingleParameter):
    type: ClassVar[ParamType] = ParamType.PATH


@dataclass(frozen=True)
class BodyParameter(param.parameters.Param):
    embed: bool = False

    @staticmethod
    def generate_alias(alias: str):
        return alias


class _BaseMultiParameter(param.parameters.Param, Generic[T]):
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


class QueriesParameter(_BaseMultiParameter[QueryParamTypes]):
    type: ClassVar[ParamType] = ParamType.QUERY


class HeadersParameter(_BaseMultiParameter[HeaderTypes]):
    type: ClassVar[ParamType] = ParamType.HEADER


class CookiesParameter(_BaseMultiParameter[CookieTypes]):
    type: ClassVar[ParamType] = ParamType.COOKIE


class PathsParameter(_BaseMultiParameter[PathParamTypes]):
    type: ClassVar[ParamType] = ParamType.PATH


@dataclass(frozen=True)
class DependencyParameter(param.parameters.Param):
    dependency: Optional[Callable] = None
    use_cache: bool = True


@dataclass(frozen=True)
class PromiseParameter(param.parameters.Param):
    promised_type: Union[None, Type[Request], Type[Response]] = None
