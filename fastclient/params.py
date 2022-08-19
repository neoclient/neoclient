from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, TypeVar, Union

from .enums import ParamType
import param
from param.sentinels import Missing, MissingType

T = TypeVar("T")


@dataclass(frozen=True)
class Param(param.ParameterSpecification[T]):
    alias: Optional[str] = None
    required: bool = False

    @staticmethod
    def generate_alias(alias: str):
        return alias


class Path(Param[T]):
    type: ParamType = ParamType.PATH

    @staticmethod
    def generate_alias(alias: str):
        return alias.lower().replace("_", "-")


class Query(Param[T]):
    type: ParamType = ParamType.QUERY

    @staticmethod
    def generate_alias(alias: str):
        return alias.lower().replace("_", "-")


class Header(Param[T]):
    type: ParamType = ParamType.HEADER

    @staticmethod
    def generate_alias(alias: str):
        return alias.title().replace("_", "-")


class Cookie(Param[T]):
    type: ParamType = ParamType.COOKIE

    @staticmethod
    def generate_alias(alias: str):
        return alias.upper()


class Body(Param[T]):
    type: ParamType = ParamType.BODY

    # TODO: Override `generate_alias` to return camel case? Or expect them to use an alias.


class Params(Param[Dict[str, Any]]):
    def __init__(
        self,
        *,
        default_factory: Union[Callable[[], Dict[str, Any]], MissingType] = Missing,
    ):
        super().__init__(
            default_factory=default_factory
            if default_factory is not Missing
            else lambda: dict()
        )


class Queries(Params):
    type: ParamType = ParamType.QUERY


class Headers(Params):
    type: ParamType = ParamType.HEADER


class Cookies(Params):
    type: ParamType = ParamType.COOKIE
