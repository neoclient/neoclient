from typing import Protocol

from fastclient import *
from fastclient.composition.composers import compose_func
from fastclient.models import RequestOptions


class Httpbin(Protocol):
    @get("/get")
    def get(self, message: int, /) -> dict:
        ...


client: FastClient = FastClient("https://httpbin.org/")
httpbin: Httpbin = client.create(Httpbin)  # type: ignore

r: RequestOptions = RequestOptions("GET", "/get")

compose_func(r, httpbin.get, ("123",), {})
# compose_func(r, httpbin.get, (), {})
