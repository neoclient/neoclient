from typing import Any, Type, TypeVar

import pydantic
from httpx import Headers, QueryParams
from pydantic import BaseModel

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


d: QueryParamTypes = parse_obj_as(QueryParamTypes, "foo")
d2: QueryParamTypes = parse_obj_as(QueryParamTypes, 123)
d3: QueryParamTypes = parse_obj_as(QueryParamTypes, QueryParams(name="sam"))
d4: QueryParamTypes = parse_obj_as(QueryParamTypes, Headers(dict(name="sam")))
