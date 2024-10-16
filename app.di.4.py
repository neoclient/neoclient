from neoclient.di import inject_request, inject_response
from neoclient.models import RequestOpts, Request, Response


# def request_dependency(headers):
#     return headers
def request_dependency(name):
    return name


# "request" injection
request_opts = RequestOpts(
    "GET",
    "/{name}",
    params={"sort": "req-asc"},
    headers={"x-source": "request-opts"},
    path_params={"name": "sam"},
)
d = inject_request(request_dependency, request_opts)


# def response_dependency(headers):
#     return headers
def response_dependency(sort):
    return sort


# "response" injection
request = Request(
    "GET",
    "/",
    params={"sort": "resp-desc"},
    headers={"x-source": "request"},
)
response = Response(
    200,
    request=request,
    headers={"x-source": "response"},
)
d2 = inject_response(response_dependency, response)
