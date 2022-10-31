import dataclasses
import inspect
import urllib.parse
from collections import Counter
from dataclasses import dataclass
from types import MethodWrapperType
from typing import (
    Any,
    Dict,
    Generic,
    Mapping,
    MutableMapping,
    Optional,
    Protocol,
    Sequence,
    Set,
    Tuple,
    TypeVar,
    runtime_checkable,
)

import httpx
import pydantic
from httpx import Client, Response
from loguru import logger
from pydantic import BaseModel
from pydantic.fields import FieldInfo, ModelField
from typing_extensions import ParamSpec

from . import api, utils
from .errors import DuplicateParameters, CompositionError
from .models import OperationSpecification, RequestOptions
from .parameters import (
    BaseParameter,
    BaseSingleParameter,
    BodyParameter,
    DependencyParameter,
    PathParameter,
    QueryParameter,
)
from .typing import Composable
from .validation import ValidatedFunction

PS = ParamSpec("PS")
RT = TypeVar("RT", covariant=True)


@runtime_checkable
class CallableWithOperation(Protocol[PS, RT]):
    operation: "Operation"

    __get__: MethodWrapperType

    def __call__(self, *args: PS.args, **kwargs: PS.kwargs) -> RT:
        ...


# NOTE: The imports are temporarily here due to cyclic dependencies
from .resolution import resolve


def get_fields(
    func: CallableWithOperation, /
) -> Mapping[str, Tuple[Any, BaseParameter]]:
    request: RequestOptions = func.operation.specification.request

    path_params: Set[str] = (
        utils.get_path_params(urllib.parse.unquote(str(request.url)))
        if request is not None
        else set()
    )

    fields: MutableMapping[str, Tuple[Any, BaseParameter]] = {}

    field_name: str
    model_field: ModelField
    for field_name, model_field in ValidatedFunction(func).model.__fields__.items():
        field_info: FieldInfo = model_field.field_info

        # Parameter Inference
        if not isinstance(field_info, BaseParameter):
            logger.info(f"Inferring parameter for field: {model_field!r}")

            if field_name in path_params:
                field_info = PathParameter(
                    alias=field_name,
                    default=BaseParameter.get_default(field_info),
                )
            elif isinstance(model_field.annotation, type) and (
                issubclass(model_field.annotation, (BaseModel, dict))
                or dataclasses.is_dataclass(model_field.annotation)
            ):
                field_info = BodyParameter(
                    alias=field_name,
                    default=BaseParameter.get_default(field_info),
                )
            else:
                field_info = QueryParameter(
                    default=BaseParameter.get_default(field_info),
                )

            logger.info(f"Inferred field {model_field!r} as parameter {field_info!r}")

        if isinstance(field_info, BaseSingleParameter) and field_info.alias is None:
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


def compose_func(
    request: RequestOptions,
    func: CallableWithOperation,
    args: Tuple[Any, ...],
    kwargs: Mapping[str, Any],
) -> None:
    logger.info(f"Composing function: {func!r}")
    logger.info(f"Initial request before composition: {request!r}")

    arguments: Mapping[str, Any] = api.bind_arguments(func, args, kwargs)

    logger.info(f"Bound arguments: {arguments!r}")

    fields: Mapping[str, Tuple[Any, BaseParameter]] = get_fields(func)

    model: BaseModel = api.create_model(func, fields, arguments)

    logger.info(f"Created model: {model!r}")

    # By this stage the arguments have been validated (coerced, defaults used, exception thrown if missing)
    validated_arguments: Mapping[str, Any] = model.dict()

    logger.info(f"Validated Arguments: {validated_arguments!r}")

    field_name: str
    model_field: ModelField
    for field_name, model_field in model.__fields__.items():
        parameter: BaseParameter = model_field.field_info
        argument: Any = validated_arguments[field_name]

        logger.debug(f"Composing parameter {parameter!r} with argument {argument!r}")

        if not isinstance(parameter, Composable):
            raise CompositionError(f"Parameter {parameter!r} is not composable")

        parameter.compose(request, argument)

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
            # request_options_with_unpopulated_url = dataclasses.replace(
            #     request_options, url=self.specification.request.url
            # )

            # return resolve_func(
            #     request_options_with_unpopulated_url,
            #     response,
            #     self.specification.response,
            #     cached_dependencies={},
            # )

            return resolve(
                response, DependencyParameter(dependency=self.specification.response)
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
