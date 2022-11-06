from typing import Any, Callable, List, Mapping, MutableMapping, Tuple, Type

from httpx import Response
from pydantic import BaseModel

from .utils import get_fields
from .. import api, utils
from ..parameters import BaseParameter

__all__: List[str] = [
    "resolve",
]


def resolve(
    func: Callable,
    response: Response,
) -> Any:
    fields: Mapping[str, Tuple[Any, BaseParameter]] = get_fields(func)

    model_cls: Type[BaseModel] = api.create_model_cls(func, fields)

    arguments: MutableMapping[str, Any] = {}

    field_name: str
    parameter: BaseParameter
    for field_name, (_, parameter) in fields.items():
        arguments[field_name] = parameter.resolve(response)

    model: BaseModel = model_cls(**arguments)

    validated_arguments: Mapping[str, Any] = model.dict()

    args: Tuple[Any, ...]
    kwargs: Mapping[str, Any]
    args, kwargs = utils.unpack_arguments(func, validated_arguments)

    return func(*args, **kwargs)
