import inspect
from typing import Any, NoReturn, Optional

from di import bind_by_type
from di.api.dependencies import DependentBase
from di.dependent import Dependent
from di.exceptions import WiringError
from httpx import URL, Headers, Request

from neoclient import Query
from neoclient.di import inject_request, inject_response, response_container
from neoclient.models import RequestOpts, Response, State

request_opts = RequestOpts(
    "GET",
    "/",
    headers={"origin": "Request!"},
    state=State({"key": "req123"}),
)
request = request_opts.build()
response = Response(
    200,
    headers={"origin": "Response!"},
    request=request,
    state=State({"key": "resp456"}),
)


def not_wirable() -> NoReturn:
    # raise WiringError("Not wirable")
    raise Exception("Not wirable")


NOT_WIRABLE = Dependent(not_wirable)


def _bind_hook(
    param: Optional[inspect.Parameter], dependent: DependentBase[Any]
) -> Optional[DependentBase[Any]]:
    print("_bind_hook", repr(param), dependent)

    if param is None:
        return None

    if param.annotation is RequestOpts:
        # return Dependent(lambda: "test")
        #     print("is request opts")
        return Dependent(RequestOpts, wire=False)
    #     # return Dependent(lambda: None, wire=True)
    #     return NOT_WIRABLE

    # raise Exception

    return None


response_container.bind(bind_by_type(Dependent(lambda: "psyche"), RequestOpts))
response_container.bind(_bind_hook)

# def my_dependency(headers: Headers, /):
#     return headers["origin"]


# def my_dependency(url: URL, /):
#     return url


# def my_dependency(state: State, /):
#     return state


# def my_dependency(name: str = Query()) -> str:
# def my_dependency(name: str) -> str:
#     return f"Hello, {name!r}"


def my_dependency(request: RequestOpts, /) -> RequestOpts:
    return request


# def my_dependency(request: Request, /) -> Request:
#     return request


# d1 = inject_request(my_dependency, request_opts)
d2 = inject_response(my_dependency, response)
