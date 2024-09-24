from httpx import URL, Headers

from neoclient.di import inject_request, inject_response
from neoclient.models import RequestOpts, Response, State

request = RequestOpts(
    "GET",
    "/",
    headers={"origin": "Request!"},
    state=State({"key": "req123"}),
)
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


def my_dependency(state: State, /):
    return state


d1 = inject_request(my_dependency, request)
d2 = inject_response(my_dependency, response)
