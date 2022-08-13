from retrofit import Retrofit, get
from typing import Protocol
from annotate import get_annotations


class HttpBinService(Protocol):
    @get("get")
    def get() -> dict:
        ...


retrofit: Retrofit = Retrofit("https://httpbin.org/")

httpbin: HttpBinService = retrofit.create(HttpBinService)

# data: dict = httpbin.get()
