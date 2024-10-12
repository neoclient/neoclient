import dataclasses
import inspect
from typing import Any, Final, Mapping, Optional, Type, TypeVar

import httpx
from di import Container, SolvedDependent, bind_by_type
from di.api.dependencies import DependentBase
from di.api.executor import SupportsSyncExecutor
from di.api.providers import DependencyProvider, DependencyProviderType
from di.dependent import Dependent
from di.executors import SyncExecutor
from pydantic import BaseModel
from pydantic.fields import FieldInfo, ModelField, Undefined

from neoclient import utils
from neoclient.params import (
    AllStateParameter,
    CookiesParameter,
    HeadersParameter,
    Parameter,
    QueryParameter,
    QueryParamsParameter,
    RequestParameter,
    ResponseParameter,
    URLParameter,
)
from neoclient.validation import create_func_model, parameter_to_model_field

from ..models import (
    URL,
    Cookies,
    Headers,
    QueryParams,
    Request,
    RequestOpts,
    Response,
    State,
)

EXECUTOR: Final[SupportsSyncExecutor] = SyncExecutor()

T = TypeVar("T")


# Common dependencies:
def _url_from_request(request: RequestOpts, /) -> URL:
    return request.url


def _params_from_url(url: URL, /) -> QueryParams:
    return url.params


# Request-scoped dependencies:
def _headers_from_request(request: RequestOpts, /) -> Headers:
    return request.headers


def _cookies_from_request(request: RequestOpts, /) -> Cookies:
    return request.cookies


def _state_from_request(request: RequestOpts, /) -> State:
    return request.state


# Response-scoped dependencies:
def _request_from_response(response: Response, /) -> Request:
    return response.request


def _headers_from_response(response: Response, /) -> Headers:
    return response.headers


def _cookies_from_response(response: Response, /) -> Cookies:
    return response.cookies


def _state_from_response(response: Response, /) -> State:
    return response.state


request_container = Container()
# neuter:
request_container.bind(bind_by_type(Dependent(RequestOpts, wire=False), RequestOpts))
request_container.bind(bind_by_type(Dependent(Response, wire=False), Response))
# common:
request_container.bind(bind_by_type(Dependent(_url_from_request), URL))
request_container.bind(bind_by_type(Dependent(_params_from_url), QueryParams))
# request:
request_container.bind(bind_by_type(Dependent(_headers_from_request), Headers))
request_container.bind(bind_by_type(Dependent(_cookies_from_request), Cookies))
request_container.bind(bind_by_type(Dependent(_state_from_request), State))

response_container = Container()
# neuter:
response_container.bind(bind_by_type(Dependent(RequestOpts, wire=False), RequestOpts))
response_container.bind(bind_by_type(Dependent(Response, wire=False), Response))
# common:
response_container.bind(bind_by_type(Dependent(_url_from_request), URL))
response_container.bind(bind_by_type(Dependent(_params_from_url), QueryParams))
# response:
response_container.bind(bind_by_type(Dependent(_request_from_response), Request))
response_container.bind(bind_by_type(Dependent(_headers_from_response), Headers))
response_container.bind(bind_by_type(Dependent(_cookies_from_response), Cookies))
response_container.bind(bind_by_type(Dependent(_state_from_response), State))


# Bind Hook(s)
# WARN: The order is important for bind hooks. Later binds take precedence.
PARAMETER_INFERENCE_LOOKUP: Mapping[Type[Any], Type[Parameter]] = {
    # RequestOpts: RequestParameter,
    # Request: RequestParameter,
    # Response: ResponseParameter,
    # httpx.Request: RequestParameter,
    # httpx.Response: ResponseParameter,
    # URL: URLParameter,
    # QueryParams: QueryParamsParameter,
    # Headers: HeadersParameter,
    # Cookies: CookiesParameter,
    # State: AllStateParameter,
}


def _bind_hook_parameter_inference(
    param: Optional[inspect.Parameter], dependent: DependentBase[Any]
) -> Optional[DependentBase[Any]]:
    print("_bind_hook_parameter_inference", repr(param), dependent)

    if param is None:
        return None

    print(param.name, param.kind, param.default, param.annotation)

    model_field: ModelField = parameter_to_model_field(param)
    field_info: FieldInfo = model_field.field_info

    print(repr(model_field), repr(model_field.annotation))

    parameter: Parameter

    # TEMP HACK
    if model_field.annotation is RequestOpts:
        # return Dependent(RequestOpts, wire=False)
        # return Dependent(lambda: None, wire=False)
        return None

    if isinstance(field_info, Parameter):
        parameter = field_info
    # elif model_field.annotation in PARAMETER_INFERENCE_LOOKUP:
    #     parameter = PARAMETER_INFERENCE_LOOKUP[model_field.annotation]()
    elif issubclass(model_field.annotation, str):  # TEMP
        parameter = QueryParameter(
            default=utils.get_default(field_info),
        )
    else:
        # raise Exception("wtf")
        return None  # assume a dep will exist for it

    # Create a clone of the parameter so that any mutations do not affect the original
    parameter_clone: Parameter = dataclasses.replace(parameter)

    parameter_clone.prepare(model_field)

    print(repr(parameter_clone), parameter_clone.alias)

    # TODO: Rename me.
    # def supply():
    #     return parameter_clone.resolve_request(...) # FIXME

    # return Dependent(lambda: f"inferred that {param.name} is a {type(parameter).__name__}")
    # return Dependent(parameter_clone.to_dependent(), wire=False)
    return Dependent(parameter_clone.to_dependent())

    # return None

    # if model_field.annotation in infer_lookup:
    #     parameter = infer_lookup[model_field.annotation]()
    # elif (
    #     (
    #         isinstance(model_field.annotation, type)
    #         and issubclass(model_field.annotation, (BaseModel, dict))
    #     )
    #     or dataclasses.is_dataclass(model_field.annotation)
    #     or (
    #         utils.is_generic_alias(model_field.annotation)
    #         and typing.get_origin(model_field.annotation)
    #         in (collections.abc.Mapping,)
    #     )
    # ):
    #     parameter = BodyParameter(
    #         default=utils.get_default(field_info),
    #     )

    # Exit, as inference not needed?
    # if isinstance(field_info, FieldInfo):
    #     return None

    # If type is obvious (e.g. Headers, Cookies)
    # ...

    # If type looks like a body parameter (e.g. is a dataclass or model)
    # ...

    # Otherwise, assume it's a query parameter
    # parameter = QueryParameter(
    #     default=utils.get_default(field_info),
    # )
    # return

    # print(repr(model_field), repr(model_field.field_info))
    # print()

    # return None


# request_container.bind(_bind_hook_parameter_inference)
# response_container.bind(_bind_hook_parameter_inference)


def _solve_and_execute(
    container: Container,
    dependent: DependencyProviderType[T],
    values: Mapping[DependencyProvider, Any] | None = None,
    *,
    use_cache: bool = True,
) -> T:
    print("solve - start")
    solved: SolvedDependent[T] = container.solve(
        Dependent(dependent, use_cache=use_cache),
        scopes=(None,),
    )
    print("solve - end")

    with container.enter_scope(None) as state:
        print("execute - start")
        tmp = solved.execute_sync(
            executor=EXECUTOR,
            state=state,
            values=values,
        )
        print("execute - end")
        return tmp


# inject, solve, execute, resolve, handle
def inject_request(
    dependent: DependencyProviderType[T],
    request: RequestOpts,
    *,
    use_cache: bool = True,
) -> T:
    return _solve_and_execute(
        request_container,
        dependent,
        {RequestOpts: request},
        use_cache=use_cache,
    )


def inject_response(
    dependent: DependencyProviderType[T],
    response: Response,
    *,
    use_cache: bool = True,
) -> T:
    return _solve_and_execute(
        response_container,
        dependent,
        {Response: response},
        use_cache=use_cache,
    )
