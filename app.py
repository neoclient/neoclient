from neoclient.di import inject_request
from neoclient.models import Headers, QueryParams, RequestOpts

r = RequestOpts("GET", "/", headers={"x-name": "bob"}, params={"age": "123"})


def foo(name: str):
    return name


d = inject_request(foo, r)
