from fastclient import FastClient, get
from fastclient.composers import timeout, headers, params, cookies, content, data, files, json

app = FastClient("https://httpbin.org/")


@headers({"X-Foo": "Bar"})
@timeout(5)
@params({"foo": "bar"})
@cookies({"cookie-name": "cookie-value"})
@content("some-content")
@data({"key": "value"})
@files({"file.txt": b"abc123"})
@json({"name": "bob"})
@app.get("/{path}")
# @get("/anything")
def foo(path: str, message: str):
    ...

d = foo("anything", "Hello, World!")