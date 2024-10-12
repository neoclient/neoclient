import inspect
from typing import Annotated, Any, Callable, Optional

from di import Container, bind_by_type
from di.api.dependencies import DependentBase
from di.dependent import Dependent, Marker
from di.executors import SyncExecutor
from httpx import Headers, Request, Response

request = Request("GET", "/", headers={"origin": "Request!"})
response = Response(200, headers={"origin": "Response!"}, request=request)

request_container = Container()
request_container.bind(bind_by_type(Dependent(Request, wire=False), Request))
request_container.bind(bind_by_type(Dependent(Response, wire=False), Response))

response_container = Container()
response_container.bind(bind_by_type(Dependent(Request, wire=False), Request))
response_container.bind(bind_by_type(Dependent(Response, wire=False), Response))


def dependency(func: Optional[Callable] = None, /, *, profile: Optional[str] = None):
    containers = {"request": request_container, "response": response_container}
    use_containers = (
        (containers[profile],) if profile is not None else containers.values()
    )

    def decorate(func):
        return_annotation = inspect.signature(func).return_annotation

        for container in use_containers:
            container.bind(bind_by_type(Dependent(func), return_annotation))

        return func

    if func is None:
        return decorate
    else:
        return decorate(func)


@dependency(profile="response")
def extract_request(response: Response, /) -> Request:
    return response.request


@dependency(profile="request")
def extract_headers_from_request(request: Request, /) -> Headers:
    return request.headers


@dependency(profile="response")
def extract_headers_from_response(response: Response, /) -> Headers:
    return response.headers


def extract_origin(headers: Headers, /) -> str:
    return headers["origin"]


# def my_dependency(origin: Annotated[str, Marker(extract_origin)], /) -> str:
#     return f"Origin: {origin}"

def my_dependency(request: Request, /) -> Request:
    return request


executor = SyncExecutor()


def solve_from_request(dependent, /) -> str:
    solved = request_container.solve(Dependent(dependent), scopes=(None,))

    with request_container.enter_scope(None) as state:
        return solved.execute_sync(
            executor=executor,
            state=state,
            values={Request: request},
        )


def solve_from_response(dependent, /) -> str:
    solved = response_container.solve(Dependent(dependent), scopes=(None,))

    with response_container.enter_scope(None) as state:
        return solved.execute_sync(
            executor=executor,
            state=state,
            values={Response: response},
        )


o1 = solve_from_request(my_dependency)
o2 = solve_from_response(my_dependency)
