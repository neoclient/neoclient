from dataclasses import dataclass
import dataclasses
from typing import (
    Any,
    Callable,
    Dict,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    Union,
)

import fastapi.encoders
import param
from pydantic import Required, BaseModel
from pydantic.fields import UndefinedType, FieldInfo, ModelField
import param.parameters
from param.errors import ResolutionError
from param.resolvers import Resolvers
from param.typing import Consumer
from param.validation import ValidatedFunction

from .models import ComposerContext, RequestOptions
from .parameters import (
    Body,
    Cookie,
    Cookies,
    Header,
    Headers,
    Path,
    Param,
    Params,
    PathParams,
    Query,
    QueryParams,
)


P = TypeVar("P", contravariant=True, bound=param.parameters.Param)


class Composer(Protocol[P]):
    def __call__(
        self,
        param: P,
        argument: Any,
    ) -> Consumer[RequestOptions]:
        ...


class ParamSetter(Protocol):
    def __call__(self, request: RequestOptions, key: str, value: Any, /) -> None:
        ...


class ParamsSetter(Protocol):
    def __call__(self, request: RequestOptions, value: Any, /) -> None:
        ...


@dataclass
class ParamsComposer(Composer[Params]):
    setter: ParamsSetter

    def __call__(
        self,
        _: Params,
        argument: Any,
    ) -> Consumer[RequestOptions]:
        def consume(request: RequestOptions, /) -> None:
            self.setter(request, argument)

        return consume


@dataclass
class ParamComposer(Composer[Param]):
    setter: ParamSetter

    def __call__(
        self,
        param: Param,
        argument: Any,
    ) -> Consumer[RequestOptions]:
        if param.alias is None:
            raise ResolutionError("Cannot compose `Param` with no alias")

        if argument is None and param.default is not Required:
            return empty_consumer

        key: str = param.alias
        value: Any = argument

        def consume(request: RequestOptions, /) -> None:
            self.setter(request, key, value)

        return consume


def empty_consumer(_: RequestOptions, /) -> None:
    pass


resolvers: Resolvers[Composer] = Resolvers({
    Query: ParamComposer(RequestOptions.add_query_param),
    Header: ParamComposer(RequestOptions.add_header),
    Cookie: ParamComposer(RequestOptions.add_cookie),
    Path: ParamComposer(RequestOptions.add_path_param),
    QueryParams: ParamsComposer(RequestOptions.add_query_params),
    Headers: ParamsComposer(RequestOptions.add_query_params),
    Cookies: ParamsComposer(RequestOptions.add_query_params),
    PathParams: ParamsComposer(RequestOptions.add_query_params),
})


# NOTE: This resolver is currently untested
# TODO: Add some middleware that sets/unsets `embed` as appropriate
@resolvers(Body)
def compose_body(
    parameter: param.Parameter,
    param: Body,
    value: Union[Any, UndefinedType],
    context: ComposerContext,
) -> None:
    true_value: Any = resolve_param(parameter, value)

    # If the param is not required and has no value, it can be omitted
    if true_value is None and param.default is not Required:
        return

    json_value: Any = fastapi.encoders.jsonable_encoder(true_value)

    total_body_params: int = len(
        [
            parameter
            for parameter in context.parameters.values()
            if type(parameter.default) is Body
        ]
    )

    embed: bool = param.embed

    if total_body_params > 1:
        embed = True

    if embed:
        if param.alias is None:
            raise ResolutionError("Cannot embed `Body` with no alias")

        json_value = {param.alias: json_value}

    # If there's only one body param, or this param shouln't be embedded in any pre-existing json,
    # make it the entire JSON request body
    if context.request.json is None or not embed:
        context.request.json = json_value
    else:
        context.request.json.update(json_value)


def get_fields(func: Callable, /) -> Dict[str, Tuple[Any, param.parameters.Param]]:
    fields: Dict[str, Tuple[Any, param.parameters.Param]] = {}

    field_name: str
    model_field: ModelField
    for field_name, model_field in ValidatedFunction(func).model.__fields__.items():
        field_info: FieldInfo = model_field.field_info

        if not isinstance(field_info, param.parameters.Param):
            field_info = Query(
                default=param.parameters.Param.get_default(field_info),
            )

        if isinstance(field_info, Param) and field_info.alias is None:
            field_info = dataclasses.replace(
                field_info, alias=field_info.generate_alias(model_field.name)
            )

        fields[field_name] = (model_field.annotation, field_info)

    return fields


def create_model(func: Callable, arguments: Dict[str, Any]) -> BaseModel:
    fields: Dict[str, Tuple[Any, param.parameters.Param]] = get_fields(func)

    class Config:
        allow_population_by_field_name = True

    model_cls: Type[BaseModel] = ValidatedFunction(func)._create_model(
        fields, config=Config
    )

    return model_cls(**arguments)


def compose_func(
    request: RequestOptions, func: Callable, arguments: Dict[str, Any]
) -> None:
    model: BaseModel = create_model(func, arguments)

    # By this stage the arguments have been validated (coerced, defaults used, exception thrown if missing)
    validated_arguments: Dict[str, Any] = model.dict()

    # TODO: Resolve here...
    field_name: str
    model_field: ModelField
    for field_name, model_field in model.__fields__.items():
        field_info: param.parameters.Param = model_field.field_info
        argument: Any = validated_arguments[field_name]

        composer: Composer = resolvers[type(field_info)]

        consumer: Consumer[RequestOptions] = composer(field_info, argument)

        consumer(request)

    # Validate the request (e.g. to ensure no path params have been missed)
    request.validate()
