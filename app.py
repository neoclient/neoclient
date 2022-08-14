from retrofit import Retrofit, get, post, get_arguments
from retrofit.models import Path, Param
from typing import Protocol
from annotate import get_annotations
import pydantic.fields
from inspect import signature


# class Path(pydantic.fields.FieldInfo): pass


class HttpBinService(Protocol):
    # @get("get")
    # def get(self) -> dict:
    #     ...

    @post("post")
    def post(self, foo: str = Param("foo")) -> dict:
        ...

    # TODO: Get this method working. Mypy complains, however it doesn't for fastapi... why??
    @get("status/{code}")
    def status(self, code: int = Path("code")) -> dict:
        ...


retrofit: Retrofit = Retrofit("https://httpbin.org/")

httpbin: HttpBinService = retrofit.create(HttpBinService)

d: dict = httpbin.status(404)

# s = signature(HttpBinService.status)
# ps = list(s.parameters.items())[1:]
# p = ps[0][1]
# p2 = ps[1][1]


# def foo(a: int, b: str, c: float = 1.0, d: tuple = ()):
#     ...

# print(get_arguments((123, "abc"), {"d": (1,2,3)}, signature(foo)))