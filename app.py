from retrofit import Retrofit, get, post, put, request
from retrofit.models import Path, Query, Header
from typing import Protocol


class HttpBinService(Protocol):
    @request("GET")
    def ip(self) -> dict:
        ...

    @get
    def headers(self, foo: str = Header("foo")) -> dict:
        ...

    @post("post")
    def post(self, foo: str = Query("foo")) -> dict:
        ...

    @put("put")
    def put(self, foo: str = "baz") -> dict:
        ...

    @get("status/{code}")
    def status(self, code: int = Path("code")) -> dict:
        ...


retrofit: Retrofit = Retrofit("https://httpbin.org/")

httpbin: HttpBinService = retrofit.create(HttpBinService)

# NOTE: This should fail
httpbin.status()
