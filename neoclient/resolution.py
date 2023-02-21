import dataclasses
from typing import Any, Callable, Mapping, MutableMapping, Optional, Tuple, Type

from httpx import URL, Cookies, Headers, QueryParams, Request, Response
from pydantic import BaseModel
from pydantic.fields import FieldInfo, ModelField

from . import api, utils
from .params import (
    BodyParameter,
    CookiesParameter,
    HeadersParameter,
    Parameter,
    QueriesParameter,
    QueryParameter,
    RequestParameter,
    ResponseParameter,
    URLParameter,
)
from .validation import ValidatedFunction


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

    return fields


def resolve(
    func: Callable,
    response: Response,
    *,
    cache: Optional[MutableMapping[Parameter, Any]] = None,
) -> Any:
    if cache is None:
        cache = {}

    fields: Mapping[str, Tuple[Any, Parameter]] = get_fields(func)

    model_cls: Type[BaseModel] = api.create_model_cls(func, fields)

    arguments: MutableMapping[str, Any] = {}

    field_name: str
    parameter: Parameter
    for field_name, (_, parameter) in fields.items():
        resolution: Any
        
        if parameter in cache:
            resolution = cache[parameter]
        else:
            # NOTE: For now, the cache is not passed deeper into the resolution process.
            # This makes the cache effective only at the first layer of resolution.
            # Ideally, the cache should be passed along, however it is only likely
            # to be of use to the `DependencyParameter` parameter.
            resolution = parameter.resolve(response)

            cache[parameter] = resolution

        arguments[field_name] = resolution

    model: BaseModel = model_cls(**arguments)

    validated_arguments: Mapping[str, Any] = model.dict()

    args: Tuple[Any, ...]
    kwargs: Mapping[str, Any]
    args, kwargs = utils.unpack_arguments(func, validated_arguments)

    return func(*args, **kwargs)
