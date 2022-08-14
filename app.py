from retrofit import Retrofit, get, post, put, request
from retrofit.models import Path, Query, Header, HeaderDict, QueryDict
from typing import Any, Dict, Protocol

"""
TODO:
    Implement `Headers`
"""


class HttpBinService(Protocol):
    @get
    def ip(self) -> dict:
        ...

    @get
    def headers(self, headers: dict = HeaderDict()) -> dict:
        ...

    @get("status/{code}")
    def status(self, code: int = Path("code")) -> dict:
        ...

    @get("get")
    def get(self, params: dict = QueryDict()) -> dict:
        ...


retrofit: Retrofit = Retrofit("https://httpbin.org/")

httpbin: HttpBinService = retrofit.create(HttpBinService)