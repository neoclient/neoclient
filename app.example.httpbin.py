from retrofit import Retrofit, get
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

httpbin: Httpbin = Retrofit("https://httpbin.org/").create(Httpbin)  # type: ignore