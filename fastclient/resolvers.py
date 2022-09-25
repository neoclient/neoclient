import inspect
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    Type,
    TypeVar,
    Union,
    Protocol,
)
import urllib.parse

import param
import param.parameters
import pydantic
import httpx
from httpx import Response
from param import ParameterType, Resolvers
from param.sentinels import Missing, MissingType

from . import api, utils
from .errors import InvalidParameterSpecification, ResolutionError
from .parameters import (
    Depends,
    PathParams,
    Promise,
    Query,
    Header,
    Cookie,
    Body,
    Param,
    QueryParams,
    Headers,
    Cookies,
    Params,
    Path,
)
from .models import RequestOptions

T = TypeVar("T")
M = TypeVar("M", bound=Mapping[str, str])


class Resolver(Protocol):
    def __call__(
        self,
        request: RequestOptions,
        response: Response,
        parameters: List[param.Parameter],
        *,
        cached_dependencies: Dict[Callable[..., Any], Any],
    ) -> Dict[str, Any]:
        ...


resolvers: Resolvers[Resolver] = Resolvers()


def _get_alias(parameter: param.Parameter[Param], /) -> str:
    if parameter.default.alias is not None:
        return parameter.default.alias
    else:
        return parameter.default.generate_alias(parameter.name)


def _parse_obj(annotation: Union[MissingType, Any], obj: Any) -> Any:
    if type(obj) is annotation or annotation in (inspect.Parameter.empty, Missing):
        return obj

    return pydantic.parse_obj_as(annotation, obj)


def _get_param(
    source: Mapping[str, str], parameters: List[param.Parameter[Param]]
) -> Dict[str, str]:
    values: Dict[str, str] = {}

    parameter: param.Parameter[Query]
    for parameter in parameters:
        value: Union[str, MissingType] = source.get(_get_alias(parameter), Missing)

        if value is not Missing:
            values[parameter.name] = value
        elif parameter.default.has_default():
            values[parameter.name] = parameter.default.get_default()
        else:
            raise ResolutionError(f"Failed to resolve parameter: {parameter!r}")

    return values


@resolvers(Query)
def resolve_response_query_param(
    request: RequestOptions,
    response: Response,
    parameters: List[param.Parameter[Query]],
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> Dict[str, str]:
    return _get_param(response.request.url.params, parameters)


@resolvers(Header)
def resolve_response_header(
    request: RequestOptions,
    response: Response,
    parameters: List[param.Parameter[Header]],
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> Dict[str, str]:
    return _get_param(response.headers, parameters)


@resolvers(Cookie)
def resolve_response_cookie(
    request: RequestOptions,
    response: Response,
    parameters: List[param.Parameter[Cookie]],
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> Dict[str, str]:
    return _get_param(response.cookies, parameters)


@resolvers(Path)
def resolve_response_path_param(
    request: RequestOptions,
    response: Response,
    parameters: List[param.Parameter[Path]],
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> Any:
    path_params: Dict[str, Any] = utils.extract_path_params(
        urllib.parse.unquote(str(request.url.copy_with(params=None, fragment=None))),
        urllib.parse.unquote(
            str(response.request.url.copy_with(params=None, fragment=None))
        ),
    )

    return _get_param(path_params, parameters)


@resolvers(Body)
def resolve_response_body(
    request: RequestOptions,
    response: Response,
    parameters: List[param.Parameter[Body]],
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> Dict[str, Any]:
    # TODO: Improve this implementation
    return {parameter.name: response.json() for parameter in parameters}


@resolvers(Promise)
def resolve_response_promise(
    request: RequestOptions,
    response: Response,
    parameters: List[param.Parameter[Promise]],
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> Dict[str, Any]:
    fullfillments: Dict[type, Any] = {
        httpx.Response: response,
        httpx.Request: response.request,
        httpx.URL: response.url,
        httpx.Headers: response.headers,
        httpx.Cookies: response.cookies,
        httpx.QueryParams: response.request.url.params,
    }

    resolved_values: Dict[str, Any] = {}

    parameter: param.Parameter[Promise]
    for parameter in parameters:
        promised_type: type

        if parameter.default.promised_type is not None:
            promised_type = parameter.default.promised_type
        elif parameter.annotation not in (inspect.Parameter.empty, Missing):
            promised_type = parameter.annotation
        else:
            raise ResolutionError(
                f"Failed to resolve parameter: {parameter!r}. Promise contains no promised type"
            )

        if promised_type in fullfillments:
            resolved_values[parameter.name] = fullfillments[promised_type]
        else:
            raise ResolutionError(
                f"Failed to resolve parameter: {parameter!r}. Unsupported promise type"
            )

    return resolved_values


def _get_params(source: M, parameters: List[param.Parameter[Params]]) -> Dict[str, M]:
    return {parameter.name: source for parameter in parameters}


@resolvers(QueryParams)
def resolve_response_query_params(
    request: RequestOptions,
    response: Response,
    parameters: List[param.Parameter[QueryParams]],
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> Dict[str, httpx.QueryParams]:
    return _get_params(response.request.url.params, parameters)


@resolvers(Headers)
def resolve_response_headers(
    request: RequestOptions,
    response: Response,
    parameters: List[param.Parameter[Headers]],
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> Dict[str, httpx.Headers]:
    return _get_params(response.headers, parameters)


@resolvers(Cookies)
def resolve_response_cookies(
    request: RequestOptions,
    response: Response,
    parameters: List[param.Parameter[Cookies]],
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> Dict[str, httpx.Cookies]:
    return _get_params(response.cookies, parameters)


@resolvers(PathParams)
def resolve_response_path_params(
    request: RequestOptions,
    response: Response,
    parameters: List[param.Parameter[PathParams]],
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> Dict[str, Dict[str, Any]]:
    path_params: Dict[str, Any] = utils.extract_path_params(
        urllib.parse.unquote(str(request.url.copy_with(params=None, fragment=None))),
        urllib.parse.unquote(
            str(response.request.url.copy_with(params=None, fragment=None))
        ),
    )

    return _get_params(path_params, parameters)


@resolvers(Depends)
def resolve_response_depends(
    request: RequestOptions,
    response: Response,
    parameters: List[param.Parameter[Depends]],
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> Dict[str, Any]:
    resolved_values: Dict[str, Any] = {}

    parameter: param.Parameter
    for parameter in parameters:
        parameter_dependency_callable: Callable

        if parameter.default.dependency is not None:
            parameter_dependency_callable = parameter.default.dependency
        elif parameter.annotation not in (inspect.Parameter.empty, Missing):
            if not callable(parameter.annotation):
                raise ResolutionError(
                    f"Failed to resolve parameter: {parameter!r}. Dependency has non-callable annotation"
                )

            parameter_dependency_callable = parameter.annotation
        else:
            raise ResolutionError(
                f"Failed to resolve parameter: {parameter!r}. Dependency is empty"
            )

        if (
            cached_dependencies is not None
            and parameter.default.use_cache
            and parameter.default.dependency in cached_dependencies
        ):
            return cached_dependencies[parameter.default.dependency]

        resolved: Any = resolve_func(
            request,
            response,
            parameter_dependency_callable,
            cached_dependencies=cached_dependencies,
        )

        # Cache resolved dependency
        cached_dependencies[parameter_dependency_callable] = resolved

        resolved_values[parameter.name] = resolved

    return resolved_values


def resolve(
    request: RequestOptions,
    response: Response,
    parameter_cls: Type[param.parameters.Param],
    parameters: List[param.Parameter],
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> Any:
    spec_type: type
    resolver: Resolver
    for spec_type, resolver in resolvers.items():
        if issubclass(parameter_cls, spec_type):
            resolved_values: Dict[str, Any] = resolver(
                request, response, parameters, cached_dependencies=cached_dependencies
            )

            return {
                parameter.name: _parse_obj(
                    parameter.annotation, resolved_values[parameter.name]
                )
                for parameter in parameters
            }

    raise InvalidParameterSpecification(f"Invalid parameter class: {parameter_cls!r}")


def aggregate_parameters(
    parameters: Dict[str, param.Parameter], /
) -> Dict[Type[param.parameters.Param], List[param.Parameter]]:
    aggregated_parameters: Dict[
        Type[param.parameters.Param], List[param.Parameter]
    ] = {}

    parameter: param.Parameter
    for parameter in parameters.values():
        aggregated_parameters.setdefault(type(parameter.default), []).append(parameter)

    return aggregated_parameters


def resolve_func(
    request: RequestOptions,
    response: Response,
    func: Callable,
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> Any:
    aggregated_parameters: Dict[
        Type[param.parameters.Param], List[param.Parameter]
    ] = aggregate_parameters(api.get_params(func, request=request))

    args: List[Any] = []
    kwargs: Dict[str, Any] = {}

    parameter_cls: Type[param.parameters.Param]
    for parameter_cls, parameters in aggregated_parameters.items():
        resolved_values: Dict[str, Any] = resolve(
            request,
            response,
            parameter_cls,
            parameters,
            cached_dependencies=cached_dependencies,
        )

        parameter: param.Parameter
        for parameter in parameters:
            value: Any = resolved_values[parameter.name]

            if parameter.type in (
                ParameterType.POSITIONAL_ONLY,
                ParameterType.VAR_POSITIONAL,
            ):
                args.append(value)
            else:
                kwargs[parameter.name] = value

    resolved: Any = func(*args, **kwargs)

    resolved = _parse_obj(inspect.signature(func).return_annotation, resolved)

    return resolved
