import dataclasses
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    Type,
    TypeVar,
)

from httpx import URL, Cookies, Headers, QueryParams, Request, Response
from pydantic import BaseModel
from pydantic.fields import FieldInfo, ModelField

from . import api, utils
from .errors import PreparationError, ResolutionError
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
from .typing import Resolver
from .validation import ValidatedFunction

T = TypeVar("T")


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
    cached_parameters: Optional[MutableMapping[Parameter, Any]] = None,
    cached_dependencies: Optional[MutableMapping[Callable, Any]] = None,
) -> Any:
    if cached_parameters is None:
        cached_parameters = {}
    if cached_dependencies is None:
        cached_dependencies = {}

    fields: Mapping[str, Tuple[Any, Parameter]] = get_fields(func)

    model_cls: Type[BaseModel] = api.create_model_cls(func, fields)

    arguments: MutableMapping[str, Any] = {}

    field_name: str
    parameter: Parameter
    for field_name, (_, parameter) in fields.items():
        resolution: Any

        if parameter in cached_parameters:
            resolution = cached_parameters[parameter]
        else:
            if isinstance(parameter, DependencyParameter):
                resolution = parameter.resolve(
                    response,
                    cached_parameters=cached_parameters,
                    cached_dependencies=cached_dependencies,
                )
            else:
                resolution = parameter.resolve(response)

            cached_parameters[parameter] = resolution

        arguments[field_name] = resolution

    model: BaseModel = model_cls(**arguments)

    validated_arguments: Mapping[str, Any] = model.dict()

    args: Tuple[Any, ...]
    kwargs: Mapping[str, Any]
    args, kwargs = utils.unpack_arguments(func, validated_arguments)

    return func(*args, **kwargs)


@dataclass
class DependencyResolver(Resolver[T]):
    dependency: Callable[..., T]

    def __call__(
        self,
        response: Response,
        /,
        *,
        cached_parameters: Optional[MutableMapping[Parameter, Any]] = None,
        cached_dependencies: Optional[MutableMapping[Callable, Any]] = None,
    ) -> T:
        return resolve(
            self.dependency,
            response,
            cached_parameters=cached_parameters,
            cached_dependencies=cached_dependencies,
        )


@dataclass(unsafe_hash=True)
class DependencyParameter(Parameter):
    dependency: Optional[Callable] = None
    use_cache: bool = True

    def resolve(
        self,
        response: Response,
        /,
        *,
        cached_parameters: Optional[MutableMapping[Parameter, Any]] = None,
        cached_dependencies: Optional[MutableMapping[Callable, Any]] = None,
    ) -> Any:
        if self.dependency is None:
            raise ResolutionError(
                f"Cannot resolve parameter {type(self)!r} without a dependency"
            )

        if cached_parameters is None:
            cached_parameters = {}
        if cached_dependencies is None:
            cached_dependencies = {}

        if self.use_cache and self.dependency in cached_dependencies:
            return cached_dependencies[self.dependency]

        resolved: Any = DependencyResolver(self.dependency)(
            response,
            cached_parameters=cached_parameters,
            cached_dependencies=cached_dependencies,
        )

        # Cache resolved dependency
        cached_dependencies[self.dependency] = resolved

        return resolved

    def prepare(self, field: ModelField, /) -> None:
        if self.dependency is None:
            if not callable(field.annotation):
                raise PreparationError(
                    f"Failed to prepare parameter: {self!r}. Dependency has non-callable annotation"
                )

            self.dependency = field.annotation
