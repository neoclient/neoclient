from fastclient import get, header, headers, query_params


@headers({"X-Bar": "x-bar"})
@header("X-Foo", "x-foo")
@query_params({"animal": "dog"})
@get("https://httpbin.org/get")
def foo(message: str) -> dict:
    ...


d = foo("hello")
