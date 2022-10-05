from dataclasses import dataclass, field
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
from param import ParameterManager, ParameterSpecification, BoundArguments, Arguments
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
from .models import RequestOptions, ResolverContext

T = TypeVar("T")
M = TypeVar("M", bound=Mapping[str, str])


class Resolver(Protocol):
    def __call__(
        self,
        parameter: param.Parameter[ParameterSpecification],
        request: RequestOptions,
        response: Response,
        # parameters: List[param.Parameter],
        # context: ResolverContext,
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


# def _get_param(
#     source: Mapping[str, str], parameters: List[param.Parameter[Param]]
# ) -> Dict[str, str]:
#     values: Dict[str, str] = {}

#     parameter: param.Parameter[Query]
#     for parameter in parameters:
#         value: Union[str, MissingType] = source.get(_get_alias(parameter), Missing)

#         if value is not Missing:
#             values[parameter.name] = value
#         elif parameter.default.has_default():
#             values[parameter.name] = parameter.default.get_default()
#         else:
#             raise ResolutionError(f"Failed to resolve parameter: {parameter!r}")

#     return values


def _get_param(source: Mapping[str, str], parameter: param.Parameter[Param]) -> str:
    value: Union[str, MissingType] = source.get(_get_alias(parameter), Missing)

    if value is not Missing:
        return value
    elif parameter.default.has_default():
        return parameter.default.get_default()
    else:
        raise ResolutionError(f"Failed to resolve parameter: {parameter!r}")


# def _get_params(source: M, parameters: List[param.Parameter[Params]]) -> Dict[str, M]:
#     return {parameter.name: source for parameter in parameters}

def _get_params(source: Mapping[str, Any], parameter: param.Parameter[Params]) -> Mapping[str, Any]:
    # TODO: Improve this implementation?
    return source


@resolvers(Query)
def resolve_response_query_param(
    parameter: param.Parameter[Query],
    request: RequestOptions,
    response: Response,
    # parameters: List[param.Parameter[Query]],
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> str:
    # return _get_param(response.request.url.params, parameters)
    return _get_param(response.request.url.params, parameter)


@resolvers(Header)
def resolve_response_header(
    parameter: param.Parameter[Header],
    request: RequestOptions,
    response: Response,
    # parameters: List[param.Parameter[Header]],
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> str:
    return _get_param(response.headers, parameter)


@resolvers(Cookie)
def resolve_response_cookie(
    parameter: param.Parameter[Cookie],
    request: RequestOptions,
    response: Response,
    # parameters: List[param.Parameter[Cookie]],
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> str:
    return _get_param(response.cookies, parameter)


@resolvers(Path)
def resolve_response_path_param(
    parameter: param.Parameter[Path],
    request: RequestOptions,
    response: Response,
    # parameters: List[param.Parameter[Path]],
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> str:
    path_params: Dict[str, str] = utils.extract_path_params(
        urllib.parse.unquote(str(request.url.copy_with(params=None, fragment=None))),
        urllib.parse.unquote(
            str(response.request.url.copy_with(params=None, fragment=None))
        ),
    )

    return _get_param(path_params, parameter)


@resolvers(QueryParams)
def resolve_response_query_params(
    parameter: param.Parameter[QueryParams],
    request: RequestOptions,
    response: Response,
    # parameters: List[param.Parameter[QueryParams]],
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> httpx.QueryParams:
    return _get_params(response.request.url.params, parameter)


@resolvers(Headers)
def resolve_response_headers(
    parameter: param.Parameter[Headers],
    request: RequestOptions,
    response: Response,
    # parameters: List[param.Parameter[Headers]],
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> httpx.Headers:
    return _get_params(response.headers, parameter)


@resolvers(Cookies)
def resolve_response_cookies(
    parameter: param.Parameter[Cookies],
    request: RequestOptions,
    response: Response,
    # parameters: List[param.Parameter[Cookies]],
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> httpx.Cookies:
    return _get_params(response.cookies, parameter)


@resolvers(PathParams)
def resolve_response_path_params(
    parameter: param.Parameter[PathParams],
    request: RequestOptions,
    response: Response,
    # parameters: List[param.Parameter[PathParams]],
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> Dict[str, str]:
    path_params: Dict[str, str] = utils.extract_path_params(
        urllib.parse.unquote(str(request.url.copy_with(params=None, fragment=None))),
        urllib.parse.unquote(
            str(response.request.url.copy_with(params=None, fragment=None))
        ),
    )

    return _get_params(path_params, parameter)

@resolvers(Body)
def resolve_response_body(
    parameter: param.Parameter[Body],
    request: RequestOptions,
    response: Response,
    # parameters: List[param.Parameter[Body]],
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> Any:
    # TODO: Improve this implementation
    return response.json()

    # return {parameter.name: response.json() for parameter in parameters}


@resolvers(Promise)
def resolve_response_promise(
    parameter: param.Parameter[Promise],
    request: RequestOptions,
    response: Response,
    # parameters: List[param.Parameter[Promise]],
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> Any:
    fullfillments: Dict[type, Any] = {
        httpx.Response: response,
        httpx.Request: response.request,
        httpx.URL: response.url,
        httpx.Headers: response.headers,
        httpx.Cookies: response.cookies,
        httpx.QueryParams: response.request.url.params,
    }

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
        return fullfillments[promised_type]
    else:
        raise ResolutionError(
            f"Failed to resolve parameter: {parameter!r}. Unsupported promise type"
        )

@resolvers(Depends)
def resolve_response_depends(
    parameter: param.Parameter[Depends],
    request: RequestOptions,
    response: Response,
    # parameters: List[param.Parameter[Depends]],
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> Any:
    # resolved_values: Dict[str, Any] = {}

    # parameter: param.Parameter
    # for parameter in parameters:
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

    return resolved

    # return resolved_values


@dataclass
class ResolutionParameterManager(ParameterManager[Resolver]):
    resolvers: Resolvers[Resolver]
    request: RequestOptions
    response: Response
    cached_dependencies: Dict[Callable[..., Any], Any] = field(default_factory=dict)

    # NOTE: Resolution parameter inference should be much more advanced than this.
    # `api.get_params` contains the current inference logic that should be used.
    def infer_spec(self, parameter: inspect.Parameter, /) -> ParameterSpecification:
        return Query(
            default=parameter.default
            if parameter.default is not inspect.Parameter.empty
            else Missing
        )

    def resolve_arguments(
        self,
        arguments: Dict[
            param.Parameter[ParameterSpecification], Union[Any, MissingType]
        ],
        /,
    ) -> Dict[str, Any]:
        resolved_arguments: Dict[str, Any] = {}

        # context: ResolverContext = ResolverContext(
        #     request=self.request, response=self.response
        # )

        parameter: param.Parameter[ParameterSpecification]
        for parameter in arguments:
            resolver: Resolver = self.get_resolver(type(parameter.default))

            # resolved_arguments[parameter.name] = resolver(parameter, context)
            resolved_arguments[parameter.name] = resolver(
                parameter,
                self.request,
                self.response,
                cached_dependencies=self.cached_dependencies,
            )

        return resolved_arguments


def resolve_func(
    request: RequestOptions,
    response: Response,
    func: Callable,
    *,
    cached_dependencies: Dict[Callable[..., Any], Any],
) -> Any:
    manager: ParameterManager[Resolver] = ResolutionParameterManager(
        resolvers=resolvers,
        request=request,
        response=response,
        cached_dependencies=cached_dependencies,
    )

    # NOTE: This was using `api.get_params` which respected the `RequestOptions` instance (for inferring path params)
    # `ResolutionParameterManager` needs to be refactored to re-support this functionality
    parameters: Dict[str, param.Parameter] = manager.get_params(func)

    args: List[MissingType] = []
    kwargs: Dict[str, MissingType] = {}

    parameter: param.Parameter
    for parameter in parameters.values():
        if parameter.type is ParameterType.POSITIONAL_ONLY:
            args.append(Missing)
        elif parameter.type in (
            ParameterType.POSITIONAL_OR_KEYWORD,
            ParameterType.KEYWORD_ONLY,
        ):
            kwargs[parameter.name] = Missing
        else:
            # TODO: Support variable parameters
            raise Exception(
                f"Currently unsupported resolver parameter type: {parameter.type!r}"
            )

    arguments: Arguments = Arguments(tuple(args), kwargs)

    resolved_arguments: BoundArguments = manager.get_arguments(func, arguments)

    resolved: Any = resolved_arguments.call(func)

    resolved = _parse_obj(inspect.signature(func).return_annotation, resolved)

    return resolved
