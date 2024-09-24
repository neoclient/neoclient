from typing import Any, Final, Mapping, TypeVar

from di import Container, SolvedDependent, bind_by_type
from di.api.executor import SupportsSyncExecutor
from di.api.providers import DependencyProvider, DependencyProviderType
from di.dependent import Dependent
from di.executors import SyncExecutor

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
request_container.bind(bind_by_type(Dependent(RequestOpts, wire=False), RequestOpts))
response_container.bind(bind_by_type(Dependent(Response, wire=False), Response))
# common:
response_container.bind(bind_by_type(Dependent(_url_from_request), URL))
response_container.bind(bind_by_type(Dependent(_params_from_url), QueryParams))
# response:
response_container.bind(bind_by_type(Dependent(_request_from_response), Request))
response_container.bind(bind_by_type(Dependent(_headers_from_response), Headers))
response_container.bind(bind_by_type(Dependent(_cookies_from_response), Cookies))
response_container.bind(bind_by_type(Dependent(_state_from_response), State))


def _solve_and_execute(
    container: Container,
    dependent: DependencyProviderType[T],
    values: Mapping[DependencyProvider, Any] | None = None,
) -> T:
    solved: SolvedDependent[T] = container.solve(
        Dependent(dependent),
        scopes=(None,),
    )

    with container.enter_scope(None) as state:
        return solved.execute_sync(
            executor=EXECUTOR,
            state=state,
            values=values,
        )


# inject, solve, execute, resolve, handle
def inject_request(dependent: DependencyProviderType[T], request: RequestOpts) -> T:
    return _solve_and_execute(
        request_container,
        dependent,
        {RequestOpts: request},
    )


def inject_response(dependent: DependencyProviderType[T], response: Response) -> T:
    return _solve_and_execute(
        response_container,
        dependent,
        {Response: response},
    )
