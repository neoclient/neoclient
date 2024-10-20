from neoclient import get, request_depends, RequestOpts
from rich.pretty import pprint

from neoclient.di import compose

request = RequestOpts("GET", "/foo")


@get("https://httpbin.org/get")
def foo(name: str): ...


compose(foo, request, ("bob",), {})
d = foo("sally")
