import dataclasses
import inspect
from dataclasses import dataclass
from types import MethodWrapperType
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Mapping,
    Optional,
    Protocol,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    runtime_checkable,
)
import urllib.parse
from collections import Counter

import httpx
import param.parameters
import pydantic
from httpx import Client, Response
from loguru import logger
from param.validation import ValidatedFunction
from pydantic import BaseModel
from pydantic.fields import FieldInfo, ModelField
from typing_extensions import ParamSpec

from . import utils
from .errors import DuplicateParameters
from .models import OperationSpecification, RequestOptions
from .parameters import (
    _BaseSingleParameter,
    QueryParameter,
    PathParameter,
    BodyParameter,
)
from .resolution.resolvers import resolve_func

PS = ParamSpec("PS")
RT = TypeVar("RT", covariant=True)


@runtime_checkable
class CallableWithOperation(Protocol[PS, RT]):
    operation: "Operation"

    __get__: MethodWrapperType

    def __call__(self, *args: PS.args, **kwargs: PS.kwargs) -> RT:
        ...

# NOTE: Temporarily here due to a cyclic dependency
from .composition import compose

def get_fields(
    func: CallableWithOperation, /
) -> Dict[str, Tuple[Any, param.parameters.Param]]:
    request: RequestOptions = func.operation.specification.request

    path_params: Set[str] = (
        utils.get_path_params(urllib.parse.unquote(str(request.url)))
        if request is not None
        else set()
    )

    fields: Dict[str, Tuple[Any, param.parameters.Param]] = {}

    field_name: str
    model_field: ModelField
    for field_name, model_field in ValidatedFunction(func).model.__fields__.items():
        field_info: FieldInfo = model_field.field_info

        # Parameter Inference
        if not isinstance(field_info, param.parameters.Param):
            logger.info(f"Inferring parameter for field: {model_field!r}")

            if field_name in path_params:
                field_info = PathParameter(
                    alias=field_name,
                    default=param.parameters.Param.get_default(field_info),
                )
            elif isinstance(model_field.annotation, type) and (
                issubclass(model_field.annotation, (BaseModel, dict))
                or dataclasses.is_dataclass(model_field.annotation)
            ):
                field_info = BodyParameter(
                    alias=field_name,
                    default=param.parameters.Param.get_default(field_info),
                )
            else:
                field_info = QueryParameter(
                    default=param.parameters.Param.get_default(field_info),
                )

            logger.info(f"Inferred field {model_field!r} as parameter {field_info!r}")

        if isinstance(field_info, _BaseSingleParameter) and field_info.alias is None:
            field_info = dataclasses.replace(
                field_info, alias=field_info.generate_alias(model_field.name)
            )

        fields[field_name] = (model_field.annotation, field_info)

    total_body_fields: int = sum(
        isinstance(field_info, BodyParameter) for _, field_info in fields.values()
    )

    if total_body_fields > 1:
        field: str
        annotation: Any
        parameter: FieldInfo
        for field, (annotation, parameter) in fields.items():
            if not isinstance(parameter, BodyParameter):
                continue

            parameter = dataclasses.replace(parameter, embed=True)

            fields[field] = (annotation, parameter)

    # Validate that there are no parameters using the same alias
    #   For example, the following function should fail validation:
    #       @get("/")
    #       def foo(a: str = Query(alias="name"), b: str = Query(alias="name")): ...
    aliases: Sequence[str] = [parameter.alias for _, parameter in fields.values()]
    alias_counts: Mapping[str, int] = Counter(aliases)
    duplicate_aliases: Set[str] = {
        alias for alias, count in alias_counts.items() if count > 1
    }
    if duplicate_aliases:
        raise DuplicateParameters(f"Duplicate parameters: {duplicate_aliases!r}")

    return fields


def create_model_cls(func: CallableWithOperation, /) -> Type[BaseModel]:
    class Config:
        allow_population_by_field_name: bool = True
        arbitrary_types_allowed: bool = True

    fields: Dict[str, Tuple[Any, param.parameters.Param]] = get_fields(func)

    return ValidatedFunction(func)._create_model(fields, config=Config)


def create_model(func: CallableWithOperation, arguments: Dict[str, Any]) -> BaseModel:
    model_cls: Type[BaseModel] = create_model_cls(func)

    return model_cls(**arguments)


def bind_arguments(
    func: CallableWithOperation, args: Tuple[Any, ...], kwargs: Dict[str, Any]
) -> Dict[str, Any]:
    arguments: Dict[str, Any] = utils.bind_arguments(func, args, kwargs)

    return {
        key: value
        for key, value in arguments.items()
        if not isinstance(value, param.parameters.Param)
    }


def compose_func(
    request: RequestOptions,
    func: CallableWithOperation,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
) -> None:
    logger.info(f"Composing function: {func!r}")
    logger.info(f"Initial request before composition: {request!r}")

    arguments: Dict[str, Any] = bind_arguments(func, args, kwargs)

    logger.info(f"Bound arguments: {arguments!r}")

    model: BaseModel = create_model(func, arguments)

    logger.info(f"Created model: {model!r}")

    # By this stage the arguments have been validated (coerced, defaults used, exception thrown if missing)
    validated_arguments: Dict[str, Any] = model.dict()

    logger.info(f"Validated Arguments: {validated_arguments!r}")

    field_name: str
    model_field: ModelField
    for field_name, model_field in model.__fields__.items():
        field_info: param.parameters.Param = model_field.field_info
        argument: Any = validated_arguments[field_name]

        compose(request, field_info, argument)

    logger.info(f"Request after composition: {request!r}")

    # Validate the request (e.g. to ensure no path params have been missed)
    request.validate()


@dataclass
class Operation(Generic[PS, RT]):
    func: CallableWithOperation[PS, RT]
    specification: OperationSpecification
    client: Optional[Client]

    def __call__(self, *args: PS.args, **kwargs: PS.kwargs) -> Any:
        request_options: RequestOptions = self.specification.request.merge(
            RequestOptions(
                method=self.specification.request.method,
                url=self.specification.request.url,
            )
        )

        compose_func(request_options, self.func, args, kwargs)

        request: httpx.Request = request_options.build_request(self.client)

        logger.info(f"Built httpx request: {request!r}")

        return_annotation: Any = inspect.signature(self.func).return_annotation

        if return_annotation is RequestOptions:
            return request_options
        if return_annotation is httpx.Request:
            return request

        client: Client = self.client if self.client is not None else Client()

        response: Response = client.send(request)

        if self.specification.response is not None:
            request_options_with_unpopulated_url = dataclasses.replace(
                request_options, url=self.specification.request.url
            )

            return resolve_func(
                request_options_with_unpopulated_url,
                response,
                self.specification.response,
                cached_dependencies={},
            )

        if return_annotation is inspect.Parameter.empty:
            return response.json()
        if return_annotation is None:
            return None
        if return_annotation is Response:
            return response
        if isinstance(return_annotation, type) and issubclass(
            return_annotation, BaseModel
        ):
            return return_annotation.parse_obj(response.json())

        return pydantic.parse_raw_as(return_annotation, response.text)
