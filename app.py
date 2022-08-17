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


retrofit: FastClient = FastClient("https://httpbin.org/")

httpbin: Httpbin = retrofit.create(Httpbin)  # type: ignore
