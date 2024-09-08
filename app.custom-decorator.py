from dataclasses import dataclass

from neoclient import get
from neoclient.decorators.api2 import RequestConsumer, build_decorator
from neoclient.models import RequestOptions

"""
TODO: Write up documentation on how to create your own decorator.

This is helpful to simplify the decorator API, to make it approachable
to humans.

Decorators can either be applied to an operation or a service

class MyDecorator(Decorator):
    def handle_request(self, request):
        request.headers["name"] = "bob"
"""


def with_referer(referer: str, /):
    def apply(request):
        request.headers["referer"] = referer

    return apply


@dataclass
class RefererHeaderConsumer(RequestConsumer):
    referer: str

    def consume_request(self, request: RequestOptions, /):
        request.headers["referer"] = self.referer


def referer(referer: str, /):
    return build_decorator(RefererHeaderConsumer(referer))


@referer("https://www.google.com/")
@get("https://httpbin.org/headers")
def headers(): ...
