from typing import Any, Optional, Type, TypeVar

from pydantic import BaseConfig, BaseModel, create_model
from pydantic.typing import display_as_type

T = TypeVar("T")


def _generate_parsing_type_name(type_: Any, /) -> str:
    return f"ParsingModel[{display_as_type(type_)}]"


def _parse_obj_as(
    type_: Type[T], obj: Any, /, *, config: Optional[Type[BaseConfig]] = None
) -> T:
    model_cls: Type[BaseModel] = create_model(
        _generate_parsing_type_name(type_),
        __config__=config,
        __root__=(type_, ...),
    )

    model: BaseModel = model_cls(__root__=obj)

    return getattr(model, "__root__")


def parse_obj_as(type_: Type[T], obj: Any) -> T:
    class Config(BaseConfig):
        arbitrary_types_allowed: bool = True

    return _parse_obj_as(type_, obj, config=Config)
