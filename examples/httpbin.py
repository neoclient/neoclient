from fastclient import FastClient, get
from typing import Protocol
from pydantic import BaseModel

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