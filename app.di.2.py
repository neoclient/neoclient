from typing import Any

from di import Container, bind_by_type
from di.api.dependencies import DependentBase
from di.dependent import Dependent
from di.executors import SyncExecutor
from httpx import Headers, Request, Response

request = Request("GET", "/", headers={"origin": "Request!"})
response = Response(200, headers={"origin": "Response!"})


def extract_request(response: Response, /) -> Request:
    return response.request


def extract_headers_from_request(request: Request, /) -> Headers:
    return request.headers


def extract_headers_from_response(response: Response, /) -> Headers:
    return response.headers


def extract_origin(headers: Headers, /) -> str:
    return headers["origin"]


def build_request_container() -> Container:
    container = Container()

    container.bind(bind_by_type(Dependent(Request, wire=False), Request))

    container.bind(bind_by_type(Dependent(extract_headers_from_request), Headers))

    return container


def build_response_container() -> Container:
    container = Container()

    container.bind(bind_by_type(Dependent(Response, wire=False), Response))
    container.bind(bind_by_type(Dependent(extract_request), Request))

    container.bind(bind_by_type(Dependent(extract_headers_from_response), Headers))

    return container


request_container = build_request_container()
response_container = build_response_container()
executor = SyncExecutor()


def solve_from_request(dependent: DependentBase[Any], /) -> str:
    solved = request_container.solve(Dependent(dependent), scopes=(None,))

    with request_container.enter_scope(None) as state:
        return solved.execute_sync(
            executor=executor,
            state=state,
            values={Request: request},
        )


def solve_from_response(dependent: DependentBase[Any], /) -> str:
    solved = response_container.solve(Dependent(dependent), scopes=(None,))

    with response_container.enter_scope(None) as state:
        return solved.execute_sync(
            executor=executor,
            state=state,
            values={Response: response},
        )


o1 = solve_from_request(extract_origin)
o2 = solve_from_response(extract_origin)
