from typing import Protocol

from pydantic import BaseModel
from rich.pretty import pprint

from fastclient import FastClient, get


class Response(BaseModel):
    args: dict
    headers: dict
    origin: str
    url: str


class Httpbin(Protocol):
    @get("/get")
    def get(self, message: str) -> Response:
        ...


fastclient: FastClient = FastClient("https://httpbin.org/")

httpbin: Httpbin = fastclient.create(Httpbin)  # type: ignore

response: Response = httpbin.get("Hello, World!")

pprint(response)
