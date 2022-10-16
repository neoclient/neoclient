from dataclasses import dataclass
import dataclasses
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Optional,
    Protocol,
    Tuple,
    Type,
    Union,
)

import fastapi.encoders
import param
from pydantic import Required, BaseModel
from pydantic.fields import UndefinedType, FieldInfo, ModelField
from param import Resolvable
import param.parameters
from param.errors import ResolutionError
from param.manager import ParameterManager
from param.models import Arguments
from param.resolvers import Resolvers, resolve_param
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


class Resolver(Protocol):
    def __call__(
        self,
        param: param.parameters.Param,
        argument: Union[Any, UndefinedType],
    ) -> Any:
        ...


class Composer(Protocol):
    def __call__(
        self,
        param: param.parameters.Param,
        argument: Union[Any, UndefinedType],
    ) -> Consumer[RequestOptions]:
        ...


class ParamSetter(Protocol):
    def __call__(self, request: RequestOptions, key: str, value: Any, /) -> None:
        ...


class ParamsSetter(Protocol):
    def __call__(self, request: RequestOptions, value: Any, /) -> None:
        ...


@dataclass(init=False)
class ParamsComposer(Consumer[RequestOptions]):
    value: Any
    setter: ParamsSetter

    def __init__(
        self,
        param: Params,
        argument: Union[Any, UndefinedType],
        setter: ParamsSetter,
    ) -> None:
        self.value = resolve_param(param, argument)
        self.setter = setter

    def __call__(self, request: RequestOptions, /) -> None:
        self.setter(request, self.value)


@dataclass(init=False)
class ParamComposer(Consumer[RequestOptions]):
    key: str
    value: Any
    required: bool
    setter: ParamSetter

    def __init__(
        self,
        param: Param,
        argument: Union[Any, UndefinedType],
        setter: ParamSetter,
    ) -> None:
        if param.alias is None:
            raise ResolutionError("Cannot compose `Param` with no alias")

        self.key: str = param.alias
        self.value: Any = resolve_param(param, argument)
        self.required = param.default is Required
        self.setter = setter

    def __call__(self, request: RequestOptions, /) -> None:
        if self.value is None and not self.required:
            return

        self.setter(request, self.key, self.value)


resolvers: Resolvers[Composer] = Resolvers()


@resolvers(Query)
def compose_query_param(
    param: Query,
    argument: Union[Any, UndefinedType],
) -> Consumer[RequestOptions]:
    return ParamComposer(
        param=param,
        argument=argument,
        setter=RequestOptions.add_query_param,
    )


@resolvers(Header)
def compose_header(
    param: Header,
    argument: Union[Any, UndefinedType],
) -> Consumer[RequestOptions]:
    return ParamComposer(
        param=param,
        argument=argument,
        setter=RequestOptions.add_header,
    )


@resolvers(Cookie)
def compose_cookie(
    param: Cookie,
    argument: Union[Any, UndefinedType],
) -> Consumer[RequestOptions]:
    return ParamComposer(
        param=param,
        argument=argument,
        setter=RequestOptions.add_cookie,
    )


@resolvers(Path)
def compose_path_param(
    param: Path,
    argument: Union[Any, UndefinedType],
) -> Consumer[RequestOptions]:
    return ParamComposer(
        param=param,
        argument=argument,
        setter=RequestOptions.add_path_param,
    )


@resolvers(QueryParams)
def compose_query_params(
    param: QueryParams,
    argument: Union[Any, UndefinedType],
) -> Consumer[RequestOptions]:
    return ParamsComposer(
        param=param,
        argument=argument,
        setter=RequestOptions.add_query_params,
    )


@resolvers(Headers)
def compose_headers(
    param: Headers,
    argument: Union[Any, UndefinedType],
) -> Consumer[RequestOptions]:
    return ParamsComposer(
        param=param,
        argument=argument,
        setter=RequestOptions.add_headers,
    )


@resolvers(Cookies)
def compose_cookies(
    param: Cookies,
    argument: Union[Any, UndefinedType],
) -> Consumer[RequestOptions]:
    return ParamsComposer(
        param=param,
        argument=argument,
        setter=RequestOptions.add_cookies,
    )


@resolvers(PathParams)
def compose_path_params(
    param: PathParams,
    argument: Union[Any, UndefinedType],
) -> Consumer[RequestOptions]:
    return ParamsComposer(
        param=param,
        argument=argument,
        setter=RequestOptions.add_path_params,
    )


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


# TODO: Wean off this
@dataclass
class CompositionParameterManager(ParameterManager[Composer]):
    resolvers: Resolvers[Composer]
    request: RequestOptions

    # NOTE: Composition parameter inference should be much more advanced than this.
    # `api.get_params` contains the current inference logic that should be used.
    def get_param(self, parameter: param.Parameter, /) -> param.parameters.Param:
        param: Optional[param.parameters.Param] = super().get_param(parameter)

        if param is not None:
            return param
        else:
            return Query(
                default=parameter.default,
            )

    def resolve_all(
        self,
        resolvables: Iterable[Resolvable],
        /,
    ) -> Dict[str, Any]:
        resolved_arguments: Dict[str, Any] = {}

        # parameters: Dict[str, param.Parameter] = {
        #     resolvable.parameter.name: resolvable.parameter
        #     for resolvable in resolvables
        # }

        resolvable: Resolvable
        for resolvable in resolvables:
            parameter: param.Parameter = resolvable.parameter
            field: param.parameters.Param = resolvable.field
            value: Union[Any, UndefinedType] = resolvable.argument

            composer: Composer = self.get_resolver(type(field))

            consumer: Consumer[RequestOptions] = composer(field, value)

            consumer(self.request)

            resolved_arguments[parameter.name] = None

        return resolved_arguments


# NOTE: DEPRECATED
def compose_func_old(
    request: RequestOptions, func: Callable, arguments: Dict[str, Any]
) -> None:
    manager: ParameterManager[Composer] = CompositionParameterManager(
        resolvers=resolvers,
        request=request,
    )

    # NOTE: `param` should complain if a param spec doesn't have a specified resolver.
    # It does not currently do this.
    manager.get_arguments(func, Arguments(kwargs=arguments))

    # Validate the request (e.g. to ensure no path params have been missed)
    request.validate()

def get_fields(func: Callable, /) -> Dict[str, Tuple[Any, Any]]:
    fields: Dict[str, Tuple[Any, Any]] = {}

    field_name: str
    model_field: ModelField
    for field_name, model_field in ValidatedFunction(func).model.__fields__.items():
        field_info: FieldInfo = model_field.field_info

        if not isinstance(field_info, param.parameters.Param):
            field_info = Query(
                default=param.parameters.Param.get_default(field_info),
            )

        if field_info.alias is None:
            field_info = dataclasses.replace(
                field_info, alias=field_info.generate_alias(model_field.name)
            )

        fields[field_name] = (model_field.annotation, field_info)

    return fields

def compose_func(
    request: RequestOptions, func: Callable, arguments: Dict[str, Any]
) -> None:
    fields: Dict[str, Tuple[Any, Any]] = get_fields(func)

    validated_function: ValidatedFunction = ValidatedFunction(func)

    # We don't want the one built for us as we need to perform param inference
    model_cls: Type[BaseModel] = validated_function._create_model(fields)

    model: BaseModel = model_cls(**arguments)

    validated_arguments: Dict[str, Any] = model.dict()

    # TODO: Resolve here...
    field_name: str
    model_field: ModelField
    for field_name, model_field in model_cls.__fields__.items():
        field_info: param.parameters.Param = model_field.field_info
        argument: Any = validated_arguments[field_name]

        composer: Composer = resolvers[type(field_info)]

        consumer: Consumer[RequestOptions] = composer(field_info, argument)

        consumer(request)

    return validated_function.prepare_arguments(validated_arguments)