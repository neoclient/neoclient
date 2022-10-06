from dataclasses import dataclass, field
import inspect
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    Set,
    Tuple,
    TypeVar,
    Union,
    Protocol,
)
import urllib.parse

import param
from param import ParameterManager, ParameterSpecification, BoundArguments, Arguments
import param.parameters
import pydantic
from pydantic import BaseModel
import httpx
from httpx import Response
from param import ParameterType, Resolvers
from param.sentinels import Missing, MissingType

from . import utils
from .errors import ResolutionError
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
    Path,
)
from .models import RequestOptions, ResolverContext

T = TypeVar("T")
M = TypeVar("M", bound=Mapping[str, Any])


class Resolver(Protocol):
    def __call__(
        self,
        parameter: param.Parameter[ParameterSpecification],
        response: Response,
        context: ResolverContext,
    ) -> Any:
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
    else:
        return pydantic.parse_obj_as(annotation, obj)


def _get_param(source: Mapping[str, T], parameter: param.Parameter[Param[T]]) -> T:
    value: Union[T, MissingType] = source.get(_get_alias(parameter), Missing)

    if value is not Missing:
        return value
    elif parameter.default.has_default():
        return parameter.default.get_default()
    else:
        raise ResolutionError(f"Failed to resolve parameter: {parameter!r}")


@resolvers(Query)
def resolve_response_query_param(
    parameter: param.Parameter[Query], response: Response, context: ResolverContext
) -> str:
    return _get_param(response.request.url.params, parameter)


@resolvers(Header)
def resolve_response_header(
    parameter: param.Parameter[Header], response: Response, context: ResolverContext
) -> str:
    return _get_param(response.headers, parameter)


@resolvers(Cookie)
def resolve_response_cookie(
    parameter: param.Parameter[Cookie], response: Response, context: ResolverContext
) -> str:
    return _get_param(response.cookies, parameter)


@resolvers(Path)
def resolve_response_path_param(
    parameter: param.Parameter[Path], response: Response, context: ResolverContext
) -> str:
    path_params: Dict[str, str] = utils.extract_path_params(
        urllib.parse.unquote(
            str(context.request.url.copy_with(params=None, fragment=None))
        ),
        urllib.parse.unquote(
            str(response.request.url.copy_with(params=None, fragment=None))
        ),
    )

    return _get_param(path_params, parameter)


@resolvers(QueryParams)
def resolve_response_query_params(
    parameter: param.Parameter[QueryParams], response: Response, context: ResolverContext
) -> httpx.QueryParams:
    return response.request.url.params


@resolvers(Headers)
def resolve_response_headers(
    parameter: param.Parameter[Headers], response: Response, context: ResolverContext
) -> httpx.Headers:
    return response.headers


@resolvers(Cookies)
def resolve_response_cookies(
    parameter: param.Parameter[Cookies], response: Response, context: ResolverContext
) -> httpx.Cookies:
    return response.cookies


@resolvers(PathParams)
def resolve_response_path_params(
    parameter: param.Parameter[PathParams], response: Response, context: ResolverContext
) -> Dict[str, str]:
    path_params: Dict[str, str] = utils.extract_path_params(
        urllib.parse.unquote(
            str(context.request.url.copy_with(params=None, fragment=None))
        ),
        urllib.parse.unquote(
            str(response.request.url.copy_with(params=None, fragment=None))
        ),
    )

    return path_params


@resolvers(Body)
def resolve_response_body(
    parameter: param.Parameter[Body], response: Response, context: ResolverContext
) -> Any:
    # TODO: Improve this implementation
    return response.json()


fullfillments: Dict[type, Callable[[Response], Any]] = {
    httpx.Response: lambda response: response,
    httpx.Request: lambda response: response.request,
    httpx.URL: lambda response: response.url,
    httpx.Headers: lambda response: response.headers,
    httpx.Cookies: lambda response: response.cookies,
    httpx.QueryParams: lambda response: response.request.url.params,
}


@resolvers(Promise)
def resolve_response_promise(
    parameter: param.Parameter[Promise], response: Response, context: ResolverContext
) -> Any:
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
        return fullfillments[promised_type](response)
    else:
        raise ResolutionError(
            f"Failed to resolve parameter: {parameter!r}. Unsupported promise type"
        )


@resolvers(Depends)
def resolve_response_depends(
    parameter: param.Parameter[Depends], response: Response, context: ResolverContext
) -> Any:
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
        context.cached_dependencies is not None
        and parameter.default.use_cache
        and parameter.default.dependency in context.cached_dependencies
    ):
        return context.cached_dependencies[parameter.default.dependency]

    resolved: Any = resolve_func(
        context.request,
        response,
        parameter_dependency_callable,
        cached_dependencies=context.cached_dependencies,
    )

    # Cache resolved dependency
    context.cached_dependencies[parameter_dependency_callable] = resolved

    return resolved


@dataclass
class ResolutionParameterManager(ParameterManager[Resolver]):
    resolvers: Resolvers[Resolver]
    request: RequestOptions
    response: Response
    cached_dependencies: Dict[Callable[..., Any], Any] = field(default_factory=dict)

    def infer_spec(self, parameter: inspect.Parameter, /) -> ParameterSpecification:
        path_params: Set[str] = (
            utils.get_path_params(urllib.parse.unquote(str(self.request.url)))
            if self.request is not None
            else set()
        )

        parameter_type: type = parameter.annotation

        body_types: Tuple[type, ...] = (BaseModel, dict)
        httpx_types: Tuple[type, ...] = (
            httpx.Headers,
            httpx.Cookies,
            httpx.QueryParams,
        )
        promise_types: Tuple[type, ...] = (
            httpx.Request,
            httpx.Response,
        )

        # NOTE: Need to check later that there's no conflict with any explicityly provided parameters
        # E.g. (path_param: str, same_path_param: str = Param(alias="path_param"))
        if parameter.name in path_params:
            return Path(
                alias=Path.generate_alias(parameter.name),
                default=(
                    parameter.default
                    if parameter.default is not parameter.empty
                    else Missing
                ),
            )
        elif (
            parameter_type is not parameter.empty
            and isinstance(parameter_type, type)
            and any(issubclass(parameter_type, body_type) for body_type in body_types)
        ):
            return Body(
                alias=Body.generate_alias(parameter.name),
                default=(
                    parameter.default
                    if parameter.default is not parameter.empty
                    else Missing
                ),
            )
        elif (
            parameter_type is not parameter.empty
            and isinstance(parameter_type, type)
            and any(
                issubclass(parameter_type, promise_type) for promise_type in promise_types
            )
        ):
            return Promise(parameter_type)
        elif (
            parameter_type is not parameter.empty
            and isinstance(parameter_type, type)
            and any(issubclass(parameter_type, httpx_type) for httpx_type in httpx_types)
        ):
            if parameter_type is httpx.Headers:
                return Headers()
            elif parameter_type is httpx.Cookies:
                return Cookies()
            elif parameter_type is httpx.QueryParams:
                return QueryParams()
            else:
                raise Exception(f"Unknown httpx dependency type: {parameter.annotation!r}")
        else:
            return Query(
                alias=Query.generate_alias(parameter.name),
                default=(
                    parameter.default
                    if parameter.default is not parameter.empty
                    else Missing
                ),
            )

    def resolve_arguments(
        self,
        arguments: Dict[
            param.Parameter[ParameterSpecification], Union[Any, MissingType]
        ],
        /,
    ) -> Dict[str, Any]:
        resolved_arguments: Dict[str, Any] = {}

        context: ResolverContext = ResolverContext(
            request=self.request,
            cached_dependencies=self.cached_dependencies,
        )

        parameter: param.Parameter[ParameterSpecification]
        for parameter in arguments:
            resolver: Resolver = self.get_resolver(type(parameter.default))

            resolved_arguments[parameter.name] = resolver(parameter, self.response, context)

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
