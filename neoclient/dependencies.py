import collections.abc
import dataclasses
import typing
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
)

import httpx
from httpx import URL, Cookies, Headers, QueryParams
from pydantic import BaseModel
from pydantic.fields import FieldInfo, ModelField

from . import api, utils
from .errors import PreparationError, ResolutionError
from .models import Request, Response
from .params import (
    BodyParameter,
    CookiesParameter,
    HeaderParameter,
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
        httpx.Request: RequestParameter,
        httpx.Response: ResponseParameter,
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
                (
                    isinstance(model_field.annotation, type)
                    and issubclass(model_field.annotation, (BaseModel, dict))
                )
                or dataclasses.is_dataclass(model_field.annotation)
                or (
                    utils.is_generic_alias(model_field.annotation)
                    and typing.get_origin(model_field.annotation)
                    in (collections.abc.Mapping,)
                )
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


@dataclass
class DependencyResolver(Resolver[T]):
    dependency: Callable[..., T]

    def __call__(
        self,
        response: Response,
        /,
        *,
        cache: Optional[MutableMapping[Parameter, Any]] = None,
    ) -> T:
        if cache is None:
            cache = {}

        fields: Mapping[str, Tuple[Any, Parameter]] = get_fields(self.dependency)

        model_cls: Type[BaseModel] = api.create_model_cls(self.dependency, fields)

        arguments: MutableMapping[str, Any] = {}

        field_name: str
        field_annotation: Any
        parameter: Parameter
        for field_name, (field_annotation, parameter) in fields.items():
            resolution: Any

            if parameter in cache:
                resolution = cache[parameter]
            else:
                cache_parameter: bool = True

                if isinstance(parameter, DependencyParameter):
                    resolution = parameter.resolve(
                        response,
                        cache=cache,
                    )

                    cache_parameter = parameter.use_cache
                else:
                    resolution = parameter.resolve(response)

                # If the parameter has a resolution function that is backed to
                # a multi-value mapping (and will yield a sequence of values),
                # inspect the field's annotation to decide whether to use the
                # entire sequence, or only the first value within in.
                if isinstance(parameter, (QueryParameter, HeaderParameter)):
                    field_annotation_origin: Optional[Any] = typing.get_origin(
                        field_annotation
                    )

                    if (
                        field_annotation is Any
                        or field_annotation not in (list, tuple)
                        and (
                            not utils.is_generic_alias(field_annotation)
                            or field_annotation_origin
                            not in (list, tuple, collections.abc.Sequence)
                        )
                    ):
                        if isinstance(resolution, Sequence) and resolution:
                            resolution = resolution[0]

                if cache_parameter:
                    cache[parameter] = resolution

            # If there is no resolution (e.g. missing header/query param etc.)
            # and the parameter has a default, then we can omit the value from
            # the arguments.
            # This is done so that Pydantic will use the default value, rather
            # than complaining that None was used.
            if resolution is None and utils.has_default(parameter):
                continue

            arguments[field_name] = resolution

        model: BaseModel = model_cls(**arguments)

        validated_arguments: Mapping[str, Any] = model.dict()

        args: Tuple[Any, ...]
        kwargs: Mapping[str, Any]
        args, kwargs = utils.unpack_arguments(self.dependency, validated_arguments)

        return self.dependency(*args, **kwargs)


@dataclass(unsafe_hash=True)
class DependencyParameter(Parameter):
    dependency: Optional[Callable] = None
    use_cache: bool = True

    def resolve(
        self,
        response: Response,
        /,
        *,
        cache: Optional[MutableMapping[Parameter, Any]] = None,
    ) -> Any:
        if self.dependency is None:
            raise ResolutionError(
                f"Cannot resolve parameter {type(self)!r} without a dependency"
            )

        return DependencyResolver(self.dependency)(response, cache=cache)

    def prepare(self, field: ModelField, /) -> None:
        if self.dependency is not None:
            return

        # NOTE: The annotation will nearly always be callable (e.g. `int`)
        # This check needs to be changed to check for non primitive callables,
        # and more generally, nothing out of the standard library.
        if not callable(field.annotation):
            raise PreparationError(
                f"Failed to prepare parameter: {self!r}. Dependency has non-callable annotation"
            )

        self.dependency = field.annotation
