from fastclient import get, api, Headers, QueryParams, Cookies
import httpx
from rich.pretty import pprint

def response(request: httpx.Request) -> dict:
    return {
        "request": request,
        # "headers": headers,
        # "query_params": query_params,
        # "cookies": cookies,
    }

@get("https://httpbin.org/ip", response=response)
def ip():
    ...

# request = ip.operation.specification.request
# resp = httpx.get("https://httpbin.org/ip")
# params = api.get_params(response, request=request)
# a = api.resolve_dependency(resp, params, request=request)
d = ip()
pprint(d)