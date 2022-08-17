from retrofit import Retrofit, get
from typing import Protocol

class Httpbin(Protocol):
    @get("/get")
    def get(self, message: str) -> dict:
        ...

httpbin: Httpbin = Retrofit("https://httpbin.org/").create(Httpbin)  # type: ignore