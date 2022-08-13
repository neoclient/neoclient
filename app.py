from retrofit import Retrofit, get, post
from typing import Protocol
from annotate import get_annotations
import pydantic.fields


class Path(pydantic.fields.FieldInfo): pass


class HttpBinService(Protocol):
    @get("get")
    def get(self) -> dict:
        ...

    @post("post")
    def post(self) -> dict:
        ...

    # TODO: Get this method working. Mypy complains, however it doesn't for fastapi... why??
    @get("status/{code}")
    def get_status(self, code: str = Path("code")) -> dict:
        ...


retrofit: Retrofit = Retrofit("https://httpbin.org/")

httpbin: HttpBinService = retrofit.create(HttpBinService)

# data: dict = httpbin.get()
