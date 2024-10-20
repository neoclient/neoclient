from neoclient import get, request_depends, RequestOpts
from rich.pretty import pprint

from neoclient.di import compose

request = RequestOpts("GET", "/foo")


@get("/foo")
def foo(name: str): ...


compose(foo, request, ("bob",), {})
