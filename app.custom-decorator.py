from dataclasses import dataclass

from neoclient import get
from neoclient.decorators.api2 import RequestConsumer, build_decorator
from neoclient.models import PreRequest

"""
TODO: Write up documentation on how to create your own decorator.

This is helpful to simplify the decorator API, to make it approachable
to humans.
"""


@dataclass
class RefererHeaderConsumer(RequestConsumer):
    referer: str

    def consume_request(self, request: PreRequest, /):
        request.headers["referer"] = self.referer


def referer(referer: str, /):
    return build_decorator(RefererHeaderConsumer(referer))


@referer("https://www.google.com/")
@get("https://httpbin.org/headers")
def headers():
    ...
