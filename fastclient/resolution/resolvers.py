import inspect
import urllib.parse
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Protocol,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

import httpx
import param
import pydantic
from httpx import Response
from param import Arguments, BoundArguments, ParameterManager, ParameterType, Resolvable
from param.errors import ResolutionError
from param.parameters import Param
from pydantic import BaseModel
from pydantic.fields import Undefined, UndefinedType
from roster import Register

from .. import utils
from ..models import RequestOptions, ResolverContext
from ..parameters import (
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
    _BaseSingleParameter,
)

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


R = TypeVar("R", bound=Resolver)


class Resolvers(Register[Type[Param], R]):
    pass


resolvers: Resolvers[Resolver] = Resolvers()


def _get_alias(parameter: param.Parameter, /) -> str:
    if not isinstance(parameter.default, _BaseSingleParameter):
        raise Exception("Cannot get alias of non-param")

    if parameter.default.alias is not None:
        return parameter.default.alias
    else:
        return parameter.default.generate_alias(parameter.name)


def _parse_obj(annotation: Union[UndefinedType, Any], obj: Any) -> Any:
    if (
        type(obj) is annotation
        or isinstance(annotation, UndefinedType)
        or annotation is inspect.Parameter.empty
    ):
        return obj
    else:
        return pydantic.parse_obj_as(annotation, obj)


def _get_param(source: Mapping[str, T], parameter: param.Parameter) -> T:
    if not isinstance(parameter.default, _BaseSingleParameter):
        raise Exception("Cannot resolve non-param")

    value: Union[T, UndefinedType] = source.get(_get_alias(parameter), Undefined)

    if not isinstance(value, UndefinedType):
        return value
    elif parameter.default.has_default():
        return parameter.default.get_default()
    else:
        raise ResolutionError(f"Failed to resolve parameter: {parameter!r}")


@resolvers(QueryParameter)
def resolve_response_query_param(
    parameter: param.Parameter, response: Response, context: ResolverContext
) -> str:
    return _get_param(response.request.url.params, parameter)


@resolvers(HeaderParameter)
def resolve_response_header(
    parameter: param.Parameter, response: Response, context: ResolverContext
) -> str:
    return _get_param(response.headers, parameter)


@resolvers(CookieParameter)
def resolve_response_cookie(
    parameter: param.Parameter, response: Response, context: ResolverContext
) -> str:
    return _get_param(response.cookies, parameter)


@resolvers(PathParameter)
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


@resolvers(QueriesParameter)
def resolve_response_query_params(
    parameter: param.Parameter, response: Response, context: ResolverContext
) -> httpx.QueryParams:
    return response.request.url.params


@resolvers(HeadersParameter)
def resolve_response_headers(
    parameter: param.Parameter, response: Response, context: ResolverContext
) -> httpx.Headers:
    return response.headers


@resolvers(CookiesParameter)
def resolve_response_cookies(
    parameter: param.Parameter, response: Response, context: ResolverContext
) -> httpx.Cookies:
    return response.cookies


@resolvers(PathsParameter)
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


@resolvers(BodyParameter)
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


@resolvers(PromiseParameter)
def resolve_response_promise(
    parameter: param.Parameter, response: Response, context: ResolverContext
) -> Any:
    if not isinstance(parameter.default, PromiseParameter):
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


@resolvers(DependencyParameter)
def resolve_response_depends(
    parameter: param.Parameter, response: Response, context: ResolverContext
) -> Any:
    if not isinstance(parameter.default, DependencyParameter):
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

    def get_param(self, parameter: param.Parameter, /) -> Param:
        param: Optional[Param] = super().get_param(parameter)

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
            return PathParameter(
                alias=PathParameter.generate_alias(parameter.name),
                default=parameter.default,
            )
        elif (
            not isinstance(parameter_type, UndefinedType)
            and isinstance(parameter_type, type)
            and any(issubclass(parameter_type, body_type) for body_type in body_types)
        ):
            return BodyParameter(
                alias=BodyParameter.generate_alias(parameter.name),
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
            return PromiseParameter(parameter_type)
        elif (
            not isinstance(parameter_type, UndefinedType)
            and isinstance(parameter_type, type)
            and any(
                issubclass(parameter_type, httpx_type) for httpx_type in httpx_types
            )
        ):
            if parameter_type is httpx.Headers:
                return HeadersParameter()
            elif parameter_type is httpx.Cookies:
                return CookiesParameter()
            elif parameter_type is httpx.QueryParams:
                return QueriesParameter()
            else:
                raise Exception(
                    f"Unknown httpx dependency type: {parameter.annotation!r}"
                )
        else:
            return QueryParameter(
                alias=QueryParameter.generate_alias(parameter.name),
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

            if not isinstance(parameter.default, Param):
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
