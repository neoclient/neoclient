from dataclasses import dataclass
from typing import Any, Generic, Type, TypeVar

from pydantic import BaseModel, BaseConfig, create_model
from pydantic.typing import display_as_type

T = TypeVar("T")


def _generate_parsing_type_name(type_: Any) -> str:
    return f"ParsingModel[{display_as_type(type_)}]"


def parse_obj_as(type_: Type[T], obj: Any, /) -> T:
    class Config(BaseConfig):
        arbitrary_types_allowed: bool = True

    model_cls: Type[BaseModel] = create_model(
        _generate_parsing_type_name(type_),
        __config__=Config,
        __root__=(type_, ...),
    )

    model: BaseModel = model_cls(__root__=obj)

    return getattr(model, "__root__")


@dataclass
class Parser(Generic[T]):
    annotation: Any

    def __call__(self, obj: Any, /) -> T:
        return parse_obj_as(self.annotation, obj)
