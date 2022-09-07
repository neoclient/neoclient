import inspect
from typing import Any, Callable, Dict, List, Optional, Union, Protocol

import param
import param.models
from param import ParameterSpecification
import pydantic
import httpx
from httpx import Response
from param import ParameterType
from param.sentinels import Missing, MissingType

from . import api
from .errors import InvalidParameterSpecification, ResolutionError
from .models import RequestOptions
from .parameters import (
    Depends,
    Promise,
    Query,
    Header,
    Cookie,
    Body,
    Param,
    QueryParams,
    Headers,
    Cookies,
)


class Resolver(Protocol):
    def __call__(
        self,
        response: Response,
        parameter: param.Parameter,
    ) -> Any:
        ...


def _get_alias(parameter: param.Parameter[Param], /) -> str:
    if parameter.spec.alias is not None:
        return parameter.spec.alias
    else:
        return parameter.spec.generate_alias(parameter.name)


def _parse_obj(annotation: Union[MissingType, Any], obj: Any) -> Any:
    if type(obj) is annotation or annotation in (inspect._empty, Missing):
        return obj

    return pydantic.parse_obj_as(annotation, obj)


def resolve_response_query_param(
    response: Response,
    parameter: param.Parameter[Query],
) -> Any:
    query_param: Union[str, MissingType] = response.request.url.params.get(
        _get_alias(parameter), Missing
    )

    if query_param is not Missing:
        return query_param
    elif parameter.spec.has_default():
        return parameter.spec.get_default()
    else:
        raise ResolutionError(f"Failed to resolve parameter: {parameter!r}")


def resolve_response_header(
    response: Response,
    parameter: param.Parameter[Header],
) -> Any:
    header: Union[str, MissingType] = response.headers.get(
        _get_alias(parameter), Missing
    )

    if header is not Missing:
        return header
    elif parameter.spec.has_default():
        return parameter.spec.get_default()
    else:
        raise ResolutionError(f"Failed to resolve parameter: {parameter!r}")


def resolve_response_cookie(
    response: Response,
    parameter: param.Parameter[Cookie],
) -> Any:
    cookie: Union[str, MissingType] = response.cookies.get(
        _get_alias(parameter), Missing
    )

    if cookie is not Missing:
        return cookie
    elif parameter.spec.has_default():
        return parameter.spec.get_default()
    else:
        raise ResolutionError(f"Failed to resolve parameter: {parameter!r}")


# def resolve_response_path_param(
#     response: Response,
#     parameter: param.Parameter[Cookie],
#     *,
#     request: Optional[RequestOptions] = None,
# ) -> Any:
#     path_params: Mapping[str, Any] = utils.extract_path_params(
#         urllib.parse.unquote(str(request.url)),
#         urllib.parse.unquote(str(response.request.url)),
#     )

#     path_param: Union[str, MissingType] = path_params.get(
#         _get_alias(parameter), Missing
#     )

#     if path_param is not Missing:
#         # return _parse_obj(parameter.annotation, path_param)
#         return path_param
#     elif parameter.spec.has_default():
#         return parameter.spec.get_default()
#     else:
#         raise ResolutionError(f"Failed to resolve parameter: {parameter!r}")


def resolve_response_body(
    response: Response,
    parameter: param.Parameter[Body],
) -> Any:
    # TODO: Massively improve this implementation
    return response.json()


# def resolve_response_params(
#     response: Response,
#     parameter: param.Parameter,
#     *,
#     request: Optional[RequestOptions] = None,
# ) -> Any:
#     spec: Params

#     if not isinstance(parameter.spec, Params):
#         raise Exception("Parameter is not a Params")
#     else:
#         spec = parameter.spec

#     return resolve_multi_param(
#         response,
#         spec,
#         annotation=parameter.annotation,
#         request=request,
#     )


# def resolve_response_depends(
#     response: Response,
#     parameter: param.Parameter,
#     *,
#     request: Optional[RequestOptions] = None,
# ) -> Any:
#     spec: Depends

#     if not isinstance(parameter.spec, Depends):
#         raise Exception("Parameter is not a Depends")
#     else:
#         spec = parameter.spec

#     return resolve_dependency(
#         response,
#         spec,
#         annotation=parameter.annotation,
#         request=request,
#     )


def resolve_response_promise(
    response: Response,
    parameter: param.Parameter[Promise],
) -> Any:
    promised_type: type

    if parameter.spec.promised_type is not None:
        promised_type = parameter.spec.promised_type
    elif parameter.annotation not in (inspect._empty, Missing):
        promised_type = parameter.annotation
    else:
        raise ResolutionError(
            f"Failed to resolve parameter: {parameter!r}. Promise contains no promised type"
        )

    if promised_type is httpx.Response:
        return response
    elif promised_type is httpx.Request:
        return response.request
    elif promised_type is httpx.URL:
        return response.url
    elif promised_type is httpx.Headers:
        return response.headers
    elif promised_type is httpx.Cookies:
        return response.cookies
    elif promised_type is httpx.QueryParams:
        return response.params
    else:
        raise ResolutionError(
            f"Failed to resolve parameter: {parameter!r}. Unsupported promise type"
        )


def resolve_response_query_params(
    response: Response,
    parameter: param.Parameter[QueryParams],
) -> Any:
    return response.params


def resolve_response_headers(
    response: Response,
    parameter: param.Parameter[Headers],
) -> Any:
    return response.headers


def resolve_response_cookies(
    response: Response,
    parameter: param.Parameter[Cookies],
) -> Any:
    return response.cookies


# def resolve_multi_param(
#     response: Response,
#     param: Params,
#     /,
#     *,
#     annotation: Union[Any, MissingType] = Missing,
#     request: Optional[RequestOptions] = None,
# ) -> Any:
#     path_params: Dict[str, Any] = (
#         utils.extract_path_params(
#             urllib.parse.unquote(
#                 str(request.url.copy_with(params=None, fragment=None))
#             ),
#             urllib.parse.unquote(
#                 str(response.request.url.copy_with(params=None, fragment=None))
#             ),
#         )
#         if request is not None
#         else {}
#     )

#     values: Dict[ParamType, Any] = {
#         ParamType.QUERY: response.url.params,
#         ParamType.HEADER: response.headers,
#         ParamType.COOKIE: response.cookies,
#         ParamType.PATH: path_params,
#     }

#     # return _parse_obj(annotation, values[param.type])
#     return values[param.type]


def resolve_response_depends(
    response: Response,
    parameter: param.Parameter[Depends],
) -> Any:
    # NOTE: What about cached dependencies?
    raise NotImplementedError


# def resolve_dependency(
#     response: Response,
#     dependency: Depends,
#     /,
#     *,
#     request: Optional[RequestOptions] = None,
#     annotation: Union[Any, MissingType] = Missing,
#     cached_dependencies: Optional[Dict[Callable[..., Any], Any]] = None,
# ) -> Any:
#     parameter_dependency_callable: Callable

#     if dependency.dependency is not None:
#         parameter_dependency_callable = dependency.dependency
#     elif annotation not in (inspect._empty, Missing):
#         if not callable(annotation):
#             raise Exception("Dependency has non-callable annotation")

#         parameter_dependency_callable = annotation
#     else:
#         raise Exception("Cannot resolve empty dependency")

#     if (
#         cached_dependencies is not None
#         and dependency.use_cache
#         and dependency.dependency in cached_dependencies
#     ):
#         return cached_dependencies[dependency.dependency]

#     parameters: Dict[str, param.Parameter] = api.get_params(
#         parameter_dependency_callable, request=request
#     )

#     args: List[Any] = []
#     kwargs: Dict[str, Any] = {}

#     if cached_dependencies is None:
#         cached_dependencies = {}

#     parameter: param.Parameter
#     for parameter in parameters.values():
#         parameter_spec: ParameterSpecification = parameter.spec

#         value: Any

#         if isinstance(parameter_spec, Depends):
#             value = resolve_dependency(
#                 response,
#                 parameter_spec,
#                 request=request,
#                 annotation=parameter.annotation,
#                 cached_dependencies=cached_dependencies,
#             )
#         else:
#             value = resolve(
#                 response,
#                 parameter,
#                 request=request,
#             )

#         if parameter.type in (
#             ParameterType.POSITIONAL_ONLY,
#             ParameterType.VAR_POSITIONAL,
#         ):
#             args.append(value)
#         else:
#             kwargs[parameter.name] = value

#     resolved: Any = parameter_dependency_callable(*args, **kwargs)

#     # Cache resolved dependency
#     cached_dependencies[parameter_dependency_callable] = resolved

#     return resolved


response_resolvers: Dict[type, Resolver] = {
    Query: resolve_response_query_param,
    Header: resolve_response_header,
    Cookie: resolve_response_cookie,
    # Path: resolve_response_path_param,
    Body: resolve_response_body,
    QueryParams: resolve_response_query_params,
    Headers: resolve_response_headers,
    Cookies: resolve_response_cookies,
    Depends: resolve_response_depends,
    Promise: resolve_response_promise,
}


def resolve(
    response: Response,
    parameter: param.Parameter,
    # *,
    # request: Optional[RequestOptions] = None,
) -> Any:
    spec_type: type
    resolver: Resolver
    for spec_type, resolver in response_resolvers.items():
        if isinstance(parameter.spec, spec_type):
            # resolved_value: Any = resolver(response, parameter, request=request)
            # resolved_value: Any = resolver(response, parameter.name, parameter.spec)
            resolved_value: Any = resolver(response, parameter)

            return _parse_obj(parameter.annotation, resolved_value)

    raise InvalidParameterSpecification(
        f"Invalid response parameter specification: {parameter.spec!r}"
    )


def resolve_func(
    response: Response,
    func: Callable,
    # /,
    # *,
    # request: Optional[RequestOptions] = None,
    # target_type: Union[Any, MissingType] = Missing,
):
    # TODO: Don't do it this way
    # return resolve_dependency(
    #     response,
    #     Depends(dependency=func),
    #     request=request,
    #     annotation=target_type,
    # )

    parameters: Dict[str, param.Parameter] = api.get_params(func)

    args: List[Any] = []
    kwargs: Dict[str, Any] = {}

    parameter: param.Parameter
    for parameter in parameters.values():
        value: Any = resolve(response, parameter)

        # if isinstance(parameter_spec, Depends):
        #     value = resolve_dependency(
        #         response,
        #         parameter_spec,
        #         request=request,
        #         annotation=parameter.annotation,
        #         cached_dependencies=cached_dependencies,
        #     )
        # else:
        #     value = resolve(
        #         response,
        #         parameter,
        #         request=request,
        #     )

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
