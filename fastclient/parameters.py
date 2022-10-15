from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    ClassVar,
    Optional,
    Type,
    Union,
)

from httpx import Request, Response
import param.parameters
from param.typing import Supplier

from .enums import ParamType


class Param(param.parameters.Param):
    type: ClassVar[ParamType]

    @staticmethod
    def generate_alias(alias: str):
        return alias


class Query(Param):
    type: ClassVar[ParamType] = ParamType.QUERY

    @staticmethod
    def generate_alias(alias: str):
        return alias.lower().replace("_", "-")


class Header(Param):
    type: ClassVar[ParamType] = ParamType.HEADER

    @staticmethod
    def generate_alias(alias: str):
        return alias.title().replace("_", "-")


class Cookie(Param):
    type: ClassVar[ParamType] = ParamType.COOKIE


class Path(Param):
    type: ClassVar[ParamType] = ParamType.PATH

    @staticmethod
    def generate_alias(alias: str):
        return alias.lower().replace("_", "-")


@dataclass(frozen=True)
class Body(param.parameters.Param):
    embed: bool = False

    @staticmethod
    def generate_alias(alias: str):
        return alias


# NOTE: Should use custom generic types for each subclass. E.g. `Headers` should have a `T` bound to `HeaderTypes`
class Params(param.parameters.Param):
    type: ClassVar[ParamType]

    def __init__(
        self,
        *,
        default_factory: Optional[Supplier[Any]] = None,
    ):
        super().__init__(
            default_factory=default_factory if default_factory is not None else dict
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
# @dataclass(frozen=True, init=False)
@dataclass(frozen=True)
class Depends(param.parameters.Param):
    dependency: Optional[Callable] = None
    use_cache: bool = True

    # def __init__(
    #     self,
    #     dependency: Optional[Callable] = None,
    #     *,
    #     use_cache: bool = True,
    # ):
    #     super().__init__()

    #     setattr(self, "dependency", dependency)
    #     setattr(self, "use_cache", use_cache)

@dataclass(frozen=True)
class Promise(param.parameters.Param):
    promised_type: Union[None, Type[Request], Type[Response]] = None
