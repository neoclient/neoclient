import dataclasses
import urllib.parse
from collections import Counter
from typing import (
    Any,
    Callable,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
    Set,
    Tuple,
)

from pydantic import BaseModel
from pydantic.fields import FieldInfo, ModelField

from . import api, utils
from .errors import DuplicateParameters
from .models import RequestOptions
from .params import BodyParameter, Parameter, PathParameter, QueryParameter
from .validation import ValidatedFunction

__all__: Sequence[str] = (
    "get_fields",
    "validate_fields",
    "compose",
)


def get_fields(
    request: RequestOptions,
    func: Callable,
) -> Mapping[str, Tuple[Any, Parameter]]:
    path_params: Set[str] = (
        utils.parse_format_string(urllib.parse.unquote(str(request.url)))
        if request is not None
        else set()
    )

    fields: MutableMapping[str, Tuple[Any, Parameter]] = {}

    field_name: str
    model_field: ModelField
    for field_name, model_field in ValidatedFunction(func).model.__fields__.items():
        field_info: FieldInfo = model_field.field_info
        parameter: Parameter

        # Parameter Inference
        if not isinstance(field_info, Parameter):
            if field_name in path_params:
                parameter = PathParameter(
                    alias=field_name,
                    default=utils.get_default(field_info),
                )
            elif isinstance(model_field.annotation, type) and (
                issubclass(model_field.annotation, (BaseModel, dict))
                or dataclasses.is_dataclass(model_field.annotation)
            ):
                parameter = BodyParameter(
                    alias=field_name,
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

    total_body_fields: int = sum(
        isinstance(parameter, BodyParameter) for _, parameter in fields.values()
    )

    if total_body_fields > 1:
        field: str
        annotation: Any
        param: Parameter
        for field, (annotation, param) in fields.items():
            if not isinstance(param, BodyParameter):
                continue

            param = dataclasses.replace(param, embed=True)

            fields[field] = (annotation, param)

    return fields


def validate_fields(fields: Mapping[str, Tuple[Any, Parameter]], /) -> None:
    parameter_aliases: MutableSequence[str] = [
        parameter.alias
        for _, parameter in fields.values()
        if parameter.alias is not None
    ]

    # Validate that there are no parameters using the same alias
    #   For example, the following function should fail validation:
    #       @get("/")
    #       def foo(a: str = Query(alias="name"), b: str = Query(alias="name")): ...
    alias_counts: Mapping[str, int] = Counter(parameter_aliases)
    duplicate_aliases: Set[str] = {
        alias for alias, count in alias_counts.items() if count > 1
    }
    if duplicate_aliases:
        raise DuplicateParameters(f"Duplicate parameters: {duplicate_aliases!r}")


def compose(
    func: Callable,
    request: RequestOptions,
    args: Tuple[Any, ...],
    kwargs: Mapping[str, Any],
) -> None:
    arguments: Mapping[str, Any] = api.bind_arguments(func, args, kwargs)

    fields: Mapping[str, Tuple[Any, Parameter]] = get_fields(request, func)

    # Validate that the fields are acceptable
    validate_fields(fields)

    model: BaseModel = api.create_model(func, fields, arguments)

    # By this stage the arguments have been validated (coerced, defaults used, exception thrown if missing)
    validated_arguments: Mapping[str, Any] = model.dict()

    field_name: str
    parameter: Parameter
    for field_name, (_, parameter) in fields.items():
        argument: Any = validated_arguments[field_name]

        parameter.compose(request, argument)

    # Validate the request (e.g. to ensure no path params have been missed)
    request.validate()
