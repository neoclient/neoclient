from dataclasses import dataclass
from typing import Any, Generic, Type, TypeVar

from pydantic import BaseModel, Field, Required, create_model

T = TypeVar("T")


def parse_obj_as(type_: Type[T], obj: Any, /) -> T:
    class BM(BaseModel):
        class Config:
            arbitrary_types_allowed: bool = True

    model_cls: Type[BaseModel] = create_model(
        "TempModel", __base__=BM, v=(type_, Field(Required))
    )

    model: BaseModel = model_cls(v=obj)

    return model.v


@dataclass
class Parser(Generic[T]):
    annotation: Any

    def __call__(self, obj: Any, /) -> T:
        return parse_obj_as(self.annotation, obj)
