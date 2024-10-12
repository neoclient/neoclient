from neoclient.di import inject_request, inject_response
from neoclient.models import RequestOpts, Request, Response


def request_dependency(headers):
    return headers


# "request" injection
request_opts = RequestOpts(
    "GET",
    "/",
    headers={"x-source": "request-opts"},
)
d = inject_request(request_dependency, request_opts)


def response_dependency(headers):
    return headers


# "response" injection
request = Request(
    "GET",
    "/",
    headers={"x-source": "request"},
)
response = Response(
    200,
    request=request,
    headers={"x-source": "response"},
)
d2 = inject_response(response_dependency, response)
