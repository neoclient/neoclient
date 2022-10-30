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
    CookieParameter,
    DependencyParameter,
    HeaderParameter,
)
from ..validation import ValidatedFunction
from .functions import (
    CookieResolutionFunction,
    DependencyResolutionFunction,
    HeaderResolutionFunction,
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


@resolvers(HeaderParameter)
def resolve_header(parameter: HeaderParameter, /) -> ResolutionFunction[Optional[str]]:
    assert parameter.alias

    return HeaderResolutionFunction(parameter.alias)


@resolvers(CookieParameter)
def resolve_cookie(parameter: CookieParameter, /) -> ResolutionFunction[Optional[str]]:
    assert parameter.alias

    return CookieResolutionFunction(parameter.alias)


def _get_fields(func: Callable, /) -> Mapping[str, Tuple[Any, BaseParameter]]:
    fields: MutableMapping[str, Tuple[Any, BaseParameter]] = {}

    field_name: str
    model_field: ModelField
    for field_name, model_field in ValidatedFunction(func).model.__fields__.items():
        field_info: FieldInfo = model_field.field_info

        # Parameter Inference
        if not isinstance(field_info, BaseParameter):
            raise NotImplementedError("TODO - Implement resolution parameter inference")

        # TODO: Add `alias` if one not specified

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
