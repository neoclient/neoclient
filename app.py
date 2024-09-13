import httpx
from neoclient import NeoClient, header, param, params
from neoclient.decorators import (
    set_header,
    add_header,
    add_param,
    set_param,
    cookie,
    headers,
    cookies,
    response,
)
from neoclient.param_functions import Headers

client = NeoClient(
    "https://httpbin.org/",
    headers={"name": "client"},
)


def response_headers(headers: httpx.Headers = Headers(), /) -> httpx.Headers:
    return headers


# @cookie("food", "chips", domain="b.com")
# @cookie("food", "pizza", domain="a.com")
# @param("action", "sleep")
# @param("action", "eat")
# @header("name", "b")
# @header("name", "a")
# @headers({"name": "bob"})
# @headers({"name": "sam"})
@response(response_headers)
@cookies({"name": "bob"})
@cookies({"name": "sam"})
@client.get("/get")
def get(): ...
