from dataclasses import dataclass, field
import inspect
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
    Protocol,
)
import urllib.parse

import param
from param import ParameterManager, BoundArguments, Arguments
import param.parameters
from param import Resolvable
from param.errors import ResolutionError
import pydantic
from pydantic import BaseModel
from pydantic.fields import Undefined, UndefinedType
import httpx
from httpx import Response
from param import ParameterType, Resolvers

from . import utils
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
        parameter: param.Parameter,
        response: Response,
        context: ResolverContext,
    ) -> Any:
        ...


resolvers: Resolvers[Resolver] = Resolvers()


def _get_alias(parameter: param.Parameter, /) -> str:
    if not isinstance(parameter.default, Param):
        raise Exception("Cannot get alias of non-param")

    if parameter.default.alias is not None:
        return parameter.default.alias
    else:
        return parameter.default.generate_alias(parameter.name)


def _parse_obj(annotation: Union[UndefinedType, Any], obj: Any) -> Any:
    if type(obj) is annotation or isinstance(annotation, UndefinedType):
        return obj
    else:
        return pydantic.parse_obj_as(annotation, obj)


def _get_param(source: Mapping[str, T], parameter: param.Parameter) -> T:
    print("_get_param:", repr(source), repr(parameter))
    if not isinstance(parameter.default, Param):
        raise Exception("Cannot resolve non-param")

    value: Union[T, UndefinedType] = source.get(_get_alias(parameter), Undefined)

    print("value:", repr(value))

    if not isinstance(value, UndefinedType):
        return value
    elif parameter.default.has_default():
        return parameter.default.get_default()
    else:
        raise ResolutionError(f"Failed to resolve parameter: {parameter!r}")


@resolvers(Query)
def resolve_response_query_param(
    parameter: param.Parameter, response: Response, context: ResolverContext
) -> str:
    return _get_param(response.request.url.params, parameter)


@resolvers(Header)
def resolve_response_header(
    parameter: param.Parameter, response: Response, context: ResolverContext
) -> str:
    return _get_param(response.headers, parameter)


@resolvers(Cookie)
def resolve_response_cookie(
    parameter: param.Parameter, response: Response, context: ResolverContext
) -> str:
    return _get_param(response.cookies, parameter)


@resolvers(Path)
def resolve_response_path_param(
    parameter: param.Parameter, response: Response, context: ResolverContext
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
    parameter: param.Parameter, response: Response, context: ResolverContext
) -> httpx.QueryParams:
    return response.request.url.params


@resolvers(Headers)
def resolve_response_headers(
    parameter: param.Parameter, response: Response, context: ResolverContext
) -> httpx.Headers:
    return response.headers


@resolvers(Cookies)
def resolve_response_cookies(
    parameter: param.Parameter, response: Response, context: ResolverContext
) -> httpx.Cookies:
    return response.cookies


@resolvers(PathParams)
def resolve_response_path_params(
    parameter: param.Parameter, response: Response, context: ResolverContext
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
    parameter: param.Parameter, response: Response, context: ResolverContext
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
    parameter: param.Parameter, response: Response, context: ResolverContext
) -> Any:
    if not isinstance(parameter.default, Promise):
        raise Exception("Cannot resolve non-param")

    promised_type: type

    if parameter.default.promised_type is not None:
        promised_type = parameter.default.promised_type
    elif not isinstance(parameter.annotation, UndefinedType):
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
    parameter: param.Parameter, response: Response, context: ResolverContext
) -> Any:
    if not isinstance(parameter.default, Depends):
        raise Exception("Cannot resolve non-dependency")

    parameter_dependency_callable: Callable

    if parameter.default.dependency is not None:
        parameter_dependency_callable = parameter.default.dependency
    elif parameter.annotation not in (inspect.Parameter.empty, Undefined):
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

    def get_param(self, parameter: param.Parameter, /) -> param.parameters.Param:
        param: Optional[param.parameters.Param] = super().get_param(parameter)

        if param is not None:
            return param

        path_params: Set[str] = (
            utils.get_path_params(urllib.parse.unquote(str(self.request.url)))
            if self.request is not None
            else set()
        )

        parameter_type: Union[Any, UndefinedType] = parameter.annotation

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
                default=parameter.default,
            )
        elif (
            not isinstance(parameter_type, UndefinedType)
            and isinstance(parameter_type, type)
            and any(issubclass(parameter_type, body_type) for body_type in body_types)
        ):
            return Body(
                alias=Body.generate_alias(parameter.name),
                default=parameter.default,
            )
        elif (
            not isinstance(parameter_type, UndefinedType)
            and isinstance(parameter_type, type)
            and any(
                issubclass(parameter_type, promise_type)
                for promise_type in promise_types
            )
        ):
            return Promise(parameter_type)
        elif (
            not isinstance(parameter_type, UndefinedType)
            and isinstance(parameter_type, type)
            and any(
                issubclass(parameter_type, httpx_type) for httpx_type in httpx_types
            )
        ):
            if parameter_type is httpx.Headers:
                return Headers()
            elif parameter_type is httpx.Cookies:
                return Cookies()
            elif parameter_type is httpx.QueryParams:
                return QueryParams()
            else:
                raise Exception(
                    f"Unknown httpx dependency type: {parameter.annotation!r}"
                )
        else:
            return Query(
                alias=Query.generate_alias(parameter.name),
                default=parameter.default,
            )

    def resolve_all(
        self,
        resolvables: Iterable[Resolvable],
        /,
    ) -> Dict[str, Any]:
        resolved_arguments: Dict[str, Any] = {}

        context: ResolverContext = ResolverContext(
            request=self.request,
            cached_dependencies=self.cached_dependencies,
        )

        resolvable: Resolvable
        for resolvable in resolvables:
            parameter: param.Parameter = resolvable.parameter

            if not isinstance(parameter.default, param.parameters.Param):
                raise Exception("Cannot resolve non-param")

            resolver: Resolver = self.get_resolver(type(parameter.default))

            resolved_arguments[parameter.name] = resolver(
                parameter, self.response, context
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
    parameters: Dict[str, param.Parameter] = manager.get_parameters(func)

    args: List[UndefinedType] = []
    kwargs: Dict[str, UndefinedType] = {}

    parameter: param.Parameter
    for parameter in parameters.values():
        if parameter.type is ParameterType.POSITIONAL_ONLY:
            args.append(Undefined)
        elif parameter.type in (
            ParameterType.POSITIONAL_OR_KEYWORD,
            ParameterType.KEYWORD_ONLY,
        ):
            kwargs[parameter.name] = Undefined
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
