from typing import Any, Callable, Mapping, Tuple, Type

from pydantic import BaseModel

from . import utils
from .parameters import BaseParameter
from .validation import ValidatedFunction


def create_model_cls(
    func: Callable, fields: Mapping[str, Tuple[Any, BaseParameter]]
) -> Type[BaseModel]:
    class Config:
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True

    return ValidatedFunction(func)._create_model(fields, config=Config)


def create_model(
    func: Callable,
    fields: Mapping[str, Tuple[Any, BaseParameter]],
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
        if not isinstance(value, BaseParameter)
    }
