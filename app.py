from neoclient.models import Headers, RequestOpts
from neoclient.di import inject_request

r = RequestOpts("GET", "/", headers={"x-name": "bob"})


def foo(headers: Headers):
    return headers


d = inject_request(foo, r)
