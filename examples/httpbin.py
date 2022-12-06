from typing import Protocol

from pydantic import BaseModel
from rich.pretty import pprint

from neoclient import FastClient, get


class Response(BaseModel):
    args: dict
    headers: dict
    origin: str
    url: str


class Httpbin(Protocol):
    @get("/get")
    def get(self, message: str) -> Response:
        ...


client: FastClient = FastClient("https://httpbin.org/")

httpbin: Httpbin = client.create(Httpbin)  # type: ignore

response: Response = httpbin.get("Hello, World!")

pprint(response)
