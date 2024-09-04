from dataclasses import dataclass

from httpx import Headers

from neoclient.decorators.api import HeadersDecorator
from neoclient import get


@dataclass
class RefererDecorator(HeadersDecorator):
    referer: str

    def decorate_headers(self, headers: Headers, /) -> None:
        headers["referer"] = self.referer


def referer(referer: str, /):
    return RefererDecorator(referer)


@referer("https://www.google.com/")
@get("https://httpbin.org/headers")
def headers():
    ...
