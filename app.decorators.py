from fastclient import get, header, headers, params


# @headers({"X-Foo": "x-bar"})
@header("X-Foo", "x-bar")
@params({"animal": "dog"})
@get("https://httpbin.org/get")
def foo(message: str) -> dict:
    ...


d = foo("hello")
