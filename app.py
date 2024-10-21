from neoclient.di import inject_request
from neoclient.models import Headers, QueryParams, RequestOpts

r = RequestOpts("GET", "/", headers={"x-name": "bob"}, params={"age": "123"})


def foo(age: int):
    return age


d = inject_request(foo, r)
