from httpx import Headers

from neoclient.decorators.api import headers_decorator
from neoclient import get


def referer(referer: str, /):
    @headers_decorator
    def decorate(headers: Headers, /) -> None:
        headers["referer"] = referer

    return decorate


@headers_decorator
def google_referer(headers: Headers, /) -> None:
    headers["referer"] = "https://www.google.com/"


@google_referer
# @referer("https://www.google.com/")
@get("https://httpbin.org/headers")
def headers():
    ...
