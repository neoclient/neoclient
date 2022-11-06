import dataclasses
from typing import Any, Callable, List, Mapping, MutableMapping, Tuple, Type

from httpx import URL, Cookies, Headers, QueryParams, Request, Response
from pydantic import BaseModel
from pydantic.fields import FieldInfo, ModelField

from .. import utils
from ..parameters import (
    Parameter,
    BodyParameter,
    CookiesParameter,
    HeadersParameter,
    QueriesParameter,
    QueryParameter,
    RequestParameter,
    ResponseParameter,
    URLParameter,
)
from ..validation import ValidatedFunction

__all__: List[str] = [
    "get_fields",
]


def get_fields(func: Callable, /) -> Mapping[str, Tuple[Any, Parameter]]:
    class Config:
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True

    httpx_lookup: Mapping[Type[Any], Type[Parameter]] = {
        Request: RequestParameter,
        Response: ResponseParameter,
        URL: URLParameter,
        QueryParams: QueriesParameter,
        Headers: HeadersParameter,
        Cookies: CookiesParameter,
    }

    fields: MutableMapping[str, Tuple[Any, Parameter]] = {}

    field_name: str
    model_field: ModelField
    for field_name, model_field in ValidatedFunction(
        func, config=Config
    ).model.__fields__.items():
        field_info: FieldInfo = model_field.field_info
        parameter: Parameter

        if not isinstance(field_info, Parameter):
            # TODO: Support inference of path parameters?

            if model_field.annotation in httpx_lookup:
                parameter = httpx_lookup[model_field.annotation]()
            elif (
                isinstance(model_field.annotation, type)
                and issubclass(model_field.annotation, (BaseModel, dict))
                or dataclasses.is_dataclass(model_field.annotation)
            ):
                parameter = BodyParameter(
                    default=utils.get_default(field_info),
                )
            else:
                parameter = QueryParameter(
                    default=utils.get_default(field_info),
                )
        else:
            parameter = field_info

        # Create a clone of the parameter so that any mutations do not affect the original
        parameter_clone: Parameter = dataclasses.replace(parameter)

        parameter_clone.prepare(model_field)

        fields[field_name] = (model_field.annotation, parameter_clone)

    # TODO: Validation? (e.g. no duplicate parameters?)

    return fields
