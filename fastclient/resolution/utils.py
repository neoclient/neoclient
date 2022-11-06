import dataclasses
from typing import Any, Callable, List, Mapping, MutableMapping, Tuple, Type

from httpx import URL, Cookies, Headers, QueryParams, Request, Response
from pydantic import BaseModel
from pydantic.fields import FieldInfo, ModelField

from .. import utils
from ..parameters import (
    BaseParameter,
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


def get_fields(func: Callable, /) -> Mapping[str, Tuple[Any, BaseParameter]]:
    class Config:
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True

    httpx_lookup: Mapping[Type[Any], Type[BaseParameter]] = {
        Request: RequestParameter,
        Response: ResponseParameter,
        URL: URLParameter,
        QueryParams: QueriesParameter,
        Headers: HeadersParameter,
        Cookies: CookiesParameter,
    }

    fields: MutableMapping[str, Tuple[Any, BaseParameter]] = {}

    field_name: str
    model_field: ModelField
    for field_name, model_field in ValidatedFunction(
        func, config=Config
    ).model.__fields__.items():
        field_info: FieldInfo = model_field.field_info
        parameter: BaseParameter

        if isinstance(field_info, BaseParameter):
            parameter = field_info
        else:
            # TODO: Support inference of path parameters

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

        parameter.prepare(model_field)

        fields[field_name] = (model_field.annotation, parameter)

    # TODO: Validation? (e.g. no duplicate parameters?)

    return fields
