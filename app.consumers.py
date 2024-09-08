from dataclasses import dataclass, field
from typing import Mapping


@dataclass
class Request:
    method: str
    url: str
    headers: Mapping[str, str] = field(default_factory=dict)


def add_referer(request: Request, /) -> None:
    request.headers["referer"] = "https://www.google.com/"


from neoclient.consumers import HeaderConsumer

add_referer = HeaderConsumer("referer", "https://www.google.com/")

from neoclient import RequestOptions

request = RequestOptions("GET", "/")

add_referer.consume_request(request)

assert request.headers == {"referer": "https://www.google.com/"}
