from typing import Any, Callable, Mapping, Tuple, Type

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from . import utils
from .validation import create_func_model


def create_model_cls(
    func: Callable, fields: Mapping[str, Tuple[Any, FieldInfo]]
) -> Type[BaseModel]:
    class Config:
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True

    return create_func_model(func, fields, config=Config)


def create_model(
    func: Callable,
    fields: Mapping[str, Tuple[Any, FieldInfo]],
    arguments: Mapping[str, Any],
) -> BaseModel:
    model_cls: Type[BaseModel] = create_model_cls(func, fields)

    return model_cls(**arguments)


def bind_arguments(
    func: Callable, args: Tuple[Any, ...], kwargs: Mapping[str, Any]
) -> Mapping[str, Any]:
    arguments: Mapping[str, Any] = utils.bind_arguments(func, args, kwargs)

    return {
        key: value
        for key, value in arguments.items()
        if not isinstance(value, FieldInfo)
    }
