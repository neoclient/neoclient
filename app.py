from dataclasses import dataclass
from typing import OrderedDict

import httpx
from httpx import Response
from pydantic import BaseModel

from fastclient import (
    Body,
    Cookie,
    Cookies,
    Depends,
    FastClient,
    Header,
    Headers,
    Path,
    PathParams,
    Promise,
    Query,
    QueryParams,
    get,
    post,
)


@dataclass
class Item:
    name: str
    price: int


class IPResponse(BaseModel):
    origin: str


app = FastClient(follow_redirects=False)

# def response(path: str = Path()) -> str:
#     return path

# def response(headers = Headers()):
#     return headers

# def response(query_params = QueryParams()):
#     return query_params


def dependency(age: int) -> int:
    return age


def response(
    # age: int = Query(),
    # server: bytes = Header(),
    # foo: str = Cookie(),
    # foo_2: str = Path(alias="foo"),
    # headers=Headers(),
    # cookies=Cookies(),
    # params=QueryParams(),
    # path_params = PathParams(),
    # body = Body(),
    request=Promise(httpx.Request),
    response=Promise(httpx.Response),
    # dependency=Depends(dependency),
):
    return dict(
        # age=age,
        # server=server,
        # foo=foo,
        # foo_2=foo_2,
        # headers=headers,
        # cookies=cookies,
        # params=params,
        # path_params=path_params,
        # body=body,
        request=request,
        response=response,
        # dependency=dependency,
    )


# def response(body: IPResponse):
#     return body


# def _response(body: IPResponse, headers: httpx.Headers = Promise(), headers_2: dict = Headers()):
#     return dict(body=body, headers=headers, headers_2=headers_2)

# def response(r = Depends(_response)):
#     return r

# def response(name: str, server: str = Header()):
#     return dict(name=name, server=server)


@app.get("https://httpbin.org/cookies/set/foo/{foo}", response=response)
# @app.get("https://httpbin.org/cookies/set/foo/{foo}")
def foo(
    age: str,
    likes: str = Header(),
    pet: str = Cookie(),
    foo: str = Path(),
    params: dict = QueryParams(),
):
    ...


# @post("https://httpbin.org/post")
# def foo(name: str = Query(), user_agent = Header(), message = Cookie(), item_a: Item = Body(), item_b: Item = Body(), query_params = QueryParams()):
#     ...

# @get("https://httpbin.org/ip", response=response)
# def get_ip():
#     ...


d = foo("43", "pizza", "cat", "bar", params={"custom-param": "custom-value"})
r = d["request"]
# d = foo(43, {"foo": "bar"})
# d = get_ip()
# d = foo("sam", "pizza!", "hello", Item("some-item", 100), Item("other-item", 50), {"age": 43})
# d = foo()
