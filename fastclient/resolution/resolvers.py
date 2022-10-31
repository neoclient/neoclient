import dataclasses
from typing import (
    Any,
    Callable,
    Mapping,
    MutableMapping,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeVar,
)

from pydantic import BaseModel
from pydantic.fields import FieldInfo, ModelField
from roster import Register

from .. import api
from ..errors import ResolutionError
from ..parameters import (
    BaseParameter,
    BaseSingleParameter,
    BodyParameter,
    CookieParameter,
    CookiesParameter,
    DependencyParameter,
    HeaderParameter,
    HeadersParameter,
    PathParameter,
    PathsParameter,
    PromiseParameter,
    QueriesParameter,
    QueryParameter,
)
from ..validation import ValidatedFunction
from .functions import (
    CookieResolutionFunction,
    CookiesResolutionFunction,
    DependencyResolutionFunction,
    HeaderResolutionFunction,
    HeadersResolutionFunction,
    QueriesResolutionFunction,
    QueryResolutionFunction,
)
from .typing import ResolutionFunction

P = TypeVar("P", contravariant=True, bound=BaseParameter)
RT = TypeVar("RT", covariant=True)


class Resolver(Protocol[P, RT]):
    def __call__(self, parameter: P, /) -> ResolutionFunction[RT]:
        ...


R = TypeVar("R", bound=Resolver)


class Resolvers(Register[Type[BaseParameter], R]):
    pass


resolvers: Resolvers[Resolver] = Resolvers()


@resolvers(QueryParameter)
def resolve_query(parameter: QueryParameter, /) -> QueryResolutionFunction:
    assert parameter.alias

    return QueryResolutionFunction(parameter.alias)


@resolvers(HeaderParameter)
def resolve_header(parameter: HeaderParameter, /) -> HeaderResolutionFunction:
    assert parameter.alias

    return HeaderResolutionFunction(parameter.alias)


@resolvers(CookieParameter)
def resolve_cookie(parameter: CookieParameter, /) -> CookieResolutionFunction:
    assert parameter.alias

    return CookieResolutionFunction(parameter.alias)


@resolvers(PathParameter)
def resolve_response_path_param(_: PathParameter, /) -> ResolutionFunction:
    raise NotImplementedError


@resolvers(QueriesParameter)
def resolve_queries(_: QueriesParameter, /) -> QueriesResolutionFunction:
    return QueriesResolutionFunction()


@resolvers(HeadersParameter)
def resolve_headers(_: HeadersParameter, /) -> HeadersResolutionFunction:
    return HeadersResolutionFunction()


@resolvers(CookiesParameter)
def resolve_cookies(_: CookiesParameter, /) -> CookiesResolutionFunction:
    return CookiesResolutionFunction()


@resolvers(PathsParameter)
def resolve_paths(_: PathsParameter, /) -> ResolutionFunction:
    raise NotImplementedError


@resolvers(BodyParameter)
def resolve_body(_: BodyParameter, /) -> ResolutionFunction:
    # TODO: Improve this implementation
    return lambda response: response.json()


@resolvers(PromiseParameter)
def resolve_promise(_: PromiseParameter, /) -> ResolutionFunction:
    raise NotImplementedError


def _get_fields(func: Callable, /) -> Mapping[str, Tuple[Any, BaseParameter]]:
    fields: MutableMapping[str, Tuple[Any, BaseParameter]] = {}

    field_name: str
    model_field: ModelField
    for field_name, model_field in ValidatedFunction(func).model.__fields__.items():
        field_info: FieldInfo = model_field.field_info

        # Parameter Inference
        if not isinstance(field_info, BaseParameter):
            # TODO: Better inference (e.g. path params)

            if isinstance(model_field.annotation, type) and (
                issubclass(model_field.annotation, (BaseModel, dict))
                or dataclasses.is_dataclass(model_field.annotation)
            ):
                field_info = BodyParameter(
                    default=BaseParameter.get_default(field_info),
                )
            else:
                field_info = QueryParameter(
                    default=BaseParameter.get_default(field_info),
                )

        # if isinstance(field_info, BaseSingleParameter) and field_info.alias is None:
        if field_info.alias is None:
            field_info = dataclasses.replace(
                field_info, alias=field_info.generate_alias(field_name)
            )

        fields[field_name] = (model_field.annotation, field_info)

    # TODO: Validation? (e.g. no duplicate parameters?)

    return fields


@resolvers(DependencyParameter)
def resolve_dependency(parameter: DependencyParameter, /) -> ResolutionFunction[Any]:
    assert parameter.dependency is not None

    fields: Mapping[str, Tuple[Any, BaseParameter]] = _get_fields(parameter.dependency)

    model_cls: Type[BaseModel] = api.create_model_cls(parameter.dependency, fields)

    resolution_functions: MutableMapping[str, ResolutionFunction] = {}

    field_name: str
    model_field: ModelField
    for field_name, model_field in model_cls.__fields__.items():
        field_info: FieldInfo = model_field.field_info

        resolver: Optional[Resolver] = resolvers.get(type(field_info))

        if resolver is None:
            raise ResolutionError(
                f"Failed to find resolver for parameter {field_info!r}"
            )

        resolution_function: ResolutionFunction = resolver(field_info)

        resolution_functions[field_name] = resolution_function

    return DependencyResolutionFunction(
        model_cls, parameter.dependency, resolution_functions
    )
