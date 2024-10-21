import collections.abc
import dataclasses
import typing
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Generic,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
)

import httpx
from httpx import URL, Cookies, Headers, QueryParams
from pydantic import BaseModel
from pydantic.fields import FieldInfo, ModelField

from neoclient.di import inject_request, inject_response

from . import api, utils
from .errors import PreparationError, ResolutionError
from .models import Request, RequestOpts, Response, State
from .params import (
    AllStateParameter,
    BodyParameter,
    CookiesParameter,
    HeaderParameter,
    HeadersParameter,
    Parameter,
    QueryParameter,
    QueryParamsParameter,
    RequestParameter,
    ResponseParameter,
    URLParameter,
)
from .validation import ValidatedFunction

T = TypeVar("T")


@dataclass
class DependencyResolver(Generic[T]):
    dependency: Callable[..., T]

    def resolve_request(
        self,
        request: RequestOpts,
        /,
        *,
        cache: Optional[MutableMapping[Parameter, Any]] = None,
    ) -> T:
        return self.resolve(request, cache=cache)

    def resolve_response(
        self,
        response: Response,
        /,
        *,
        cache: Optional[MutableMapping[Parameter, Any]] = None,
    ) -> T:
        return self.resolve(response, cache=cache)

    def resolve(
        self,
        request_or_response: Union[RequestOpts, Response],
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
                    if isinstance(request_or_response, RequestOpts):
                        resolution = parameter.resolve_request(
                            request_or_response,
                            cache=cache,
                        )
                    else:
                        resolution = parameter.resolve_response(
                            request_or_response,
                            cache=cache,
                        )

                    cache_parameter = parameter.use_cache
                else:
                    if isinstance(request_or_response, RequestOpts):
                        resolution = parameter.resolve_request(request_or_response)
                    else:
                        resolution = parameter.resolve_response(request_or_response)

                # If the parameter has a resolution function that is backed to
                # a multi-value mapping (and will yield a sequence of values),
                # inspect the field's annotation to decide whether to use the
                # entire sequence, or only the first value within it.
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
