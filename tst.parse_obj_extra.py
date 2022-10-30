from typing import Any, Type, TypeVar

import pydantic
from httpx import Headers, QueryParams
from pydantic import BaseModel
from pydantic.typing import display_as_type

from fastclient.types import QueryParamTypes

T = TypeVar("T")


def parse_obj_as(type_: Type[T], obj: Any, /) -> T:
    class BM(BaseModel):
        class Config:
            arbitrary_types_allowed: bool = True

    model_cls: Type[BaseModel] = pydantic.create_model(
        "TempModel", __base__=BM, v=(type_, pydantic.Field(pydantic.Required))
    )

    model: BaseModel = model_cls(v=obj)

    return model.v

def _generate_parsing_type_name(type_: Any) -> str:
    return f'ParsingModel[{display_as_type(type_)}]'

def parse_obj_as_2(type_: Type[T], obj: Any, /) -> T:
    class Config(pydantic.BaseConfig):
        arbitrary_types_allowed: bool = True

    model_cls: Type[BaseModel] = pydantic.create_model(
        _generate_parsing_type_name(type_),
        __config__=Config,
        __root__=(type_, ...),
    )

    model: BaseModel = model_cls(__root__=obj)

    return getattr(model, "__root__")


a: QueryParamTypes = parse_obj_as(QueryParamTypes, "foo")
a2: QueryParamTypes = parse_obj_as(QueryParamTypes, 123)
a3: QueryParamTypes = parse_obj_as(QueryParamTypes, QueryParams(name="sam"))
a4: QueryParamTypes = parse_obj_as(QueryParamTypes, Headers(dict(name="sam")))

b: QueryParamTypes = parse_obj_as_2(QueryParamTypes, "foo")
b2: QueryParamTypes = parse_obj_as_2(QueryParamTypes, 123)
b3: QueryParamTypes = parse_obj_as_2(QueryParamTypes, QueryParams(name="sam"))
b4: QueryParamTypes = parse_obj_as_2(QueryParamTypes, Headers(dict(name="sam")))
