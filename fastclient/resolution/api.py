import dataclasses
from typing import Any, Callable, Mapping, MutableMapping, Tuple, Type

from httpx import Response, Request, Headers, Cookies, QueryParams, URL
from pydantic import BaseModel
from pydantic.fields import ModelField, FieldInfo

from fastclient.errors import ResolutionError

from .. import api
from ..parameters import (
    BaseParameter,
    BodyParameter,
    QueryParameter,
    RequestParameter,
    ResponseParameter,
    URLParameter,
    QueriesParameter,
    HeadersParameter,
    CookiesParameter,
    DependencyParameter,
)
from ..validation import ValidatedFunction


def _get_fields(func: Callable, /) -> Mapping[str, Tuple[Any, BaseParameter]]:
    class Config:
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True

    fields: MutableMapping[str, Tuple[Any, BaseParameter]] = {}

    field_name: str
    model_field: ModelField
    for field_name, model_field in ValidatedFunction(func, config=Config).model.__fields__.items():
        field_info: FieldInfo = model_field.field_info
        parameter: BaseParameter

        if isinstance(field_info, BaseParameter):
            parameter = field_info
        # Parameter Inference
        else:
            # TODO: Support inference of path parameters
            # TODO: Shift responsibility of inference to parameters themselves.

            if model_field.annotation is Request:
                parameter = RequestParameter()
            elif model_field.annotation is Response:
                parameter = ResponseParameter()
            elif model_field.annotation is URL:
                parameter = URLParameter()
            elif model_field.annotation is QueryParams:
                parameter = QueriesParameter()
            elif model_field.annotation is Headers:
                parameter = HeadersParameter()
            elif model_field.annotation is Cookies:
                parameter = CookiesParameter()
            elif (
                isinstance(model_field.annotation, type)
                and issubclass(model_field.annotation, (BaseModel, dict))
                or dataclasses.is_dataclass(model_field.annotation)
            ):
                parameter = BodyParameter(
                    default=BaseParameter.get_default(field_info),
                )
            else:
                parameter = QueryParameter(
                    default=BaseParameter.get_default(field_info),
                )

        # TODO: Depends .dependency must not be None
        if isinstance(parameter, DependencyParameter) and parameter.dependency is None:
            if not callable(model_field.annotation):
                raise ResolutionError(f"Failed to resolve parameter: {parameter!r}. Dependency has non-callable annotation")
            
            parameter.dependency = model_field.annotation

        if parameter.alias is None:
            parameter = dataclasses.replace(
                parameter, alias=parameter.generate_alias(field_name)
            )

        fields[field_name] = (model_field.annotation, parameter)

    # TODO: Validation? (e.g. no duplicate parameters?)

    return fields


def resolve(
    func: Callable,
    response: Response,
) -> Any:
    fields: Mapping[str, Tuple[Any, BaseParameter]] = _get_fields(func)

    model_cls: Type[BaseModel] = api.create_model_cls(func, fields)

    arguments: MutableMapping[str, Any] = {}

    field_name: str
    model_field: ModelField
    for field_name, model_field in model_cls.__fields__.items():
        # TODO: Fix typing of this vvv (FieldInfo is not a BaseParameter)
        parameter: BaseParameter = model_field.field_info

        arguments[field_name] = parameter.resolve(response)

    model: BaseModel = model_cls(**arguments)

    validated_arguments: Mapping[str, Any] = model.dict()

    return func(**validated_arguments)
