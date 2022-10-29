from fastclient import (
    cookie,
    cookies,
    get,
    header,
    headers,
    json,
    path,
    path_params,
    query,
    query_params,
)


class Foo:
    pass


@json(123)
@path_params({"endpoint": "destroy"})
@cookies({"likes": "pizza"})
@headers({"powered-by": "chips"})
@query_params({"age": "43"})
@path("bar", "baz")
@cookie("auth-token", "abc-123")
@header("user-agent", "fastclient/1.0")
@query("name", "sam")
@get("/foo")
def foo():
    ...


r = foo.operation.specification.request
