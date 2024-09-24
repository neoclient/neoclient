import inspect
from typing import Any, NoReturn, Optional

import httpx
from di import Container, bind_by_type
from di.api.dependencies import DependentBase
from di.dependent import Dependent, Marker
from di.executors import SyncExecutor
from typing_extensions import Annotated

# class Request(httpx.Request):
#     @classmethod
#     def __di_dependency__(cls, param: inspect.Parameter) -> "Dependent[Request]":
#         # note that client is injected by di!
#         async def func(client: HTTPClient) -> B:
#             # do an http request or something
#             return Request(msg=f"👋 from {param.name}")

#         return Dependent(func)


def match_by_parameter_name(
    param: Optional[inspect.Parameter], dependent: DependentBase[Any]
) -> Optional[DependentBase[Any]]:
    print("match_by_parameter_name", param)
    if param is not None and param.name == "request":
        # return Dependent(lambda: "request!", scope=None)
        return Dependent(lambda: "request!")
    return None


def request_stub() -> httpx.Request:
    raise NotImplementedError


request = httpx.Request(
    "GET",
    "/ip",
    params={"format": "json"},
    headers={"referer": "google.com"},
)
response = httpx.Response(
    200,
    headers={"server": "nginx"},
    request=request,
)


def dep_request(response: httpx.Response, /) -> httpx.Request:
    return response.request


# def extract_headers(request: httpx.Request, /) -> httpx.Headers:
# def extract_headers(request: Annotated[httpx.Request, Marker(request_stub, wire=False)], /) -> httpx.Headers:
def extract_headers(
    request: httpx.Request,
    /,
    # r: Annotated[httpx.Request, Marker(wire=False)], /
) -> httpx.Headers:
    return request.headers


def _raise(param: Optional[inspect.Parameter], dependent: DependentBase[Any]) -> Any:
    raise RuntimeError(f"The parameter {param} to {dependent.call} is not wirable")


def _raise2() -> NoReturn:
    raise RuntimeError("Not wirable")


container = Container()
# bind_by_type
container.bind(bind_by_type(Dependent(wire=False, call=_raise2), httpx.Request))
# container.bind(bind_by_type(Dependent(wire=False, call=_raise2), httpx.Request, covariant=True))
# container.bind(match_by_parameter_name)
executor = SyncExecutor()
# solved = container.solve(Dependent(extract_headers, scope="request"), scopes=["request"])
# solved = container.solve(Dependent(extract_headers), scopes=("singleton",))
solved = container.solve(Dependent(extract_headers), scopes=(None,))
with container.enter_scope(None) as state:
    headers = solved.execute_sync(
        executor=executor, state=state, values={httpx.Request: request}
    )
