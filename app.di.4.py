from neoclient.di import inject_request
from neoclient.models import RequestOpts


def my_dependency(headers):
    return headers


request = RequestOpts(
    "GET",
    "/",
    headers={"user-agent": "bob/1.0"},
)
d = inject_request(my_dependency, request)
