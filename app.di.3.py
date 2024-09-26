from httpx import URL, Headers

from neoclient import Query
from neoclient.di import inject_request, inject_response
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


# def my_dependency(headers: Headers, /):
#     return headers["origin"]


# def my_dependency(url: URL, /):
#     return url


# def my_dependency(state: State, /):
#     return state


def my_dependency(name: str = Query()) -> str:
    return f"Hello, {name!r}"


d1 = inject_request(my_dependency, request_opts)
d2 = inject_response(my_dependency, response)
