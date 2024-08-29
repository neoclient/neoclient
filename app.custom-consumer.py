from dataclasses import dataclass

from neoclient.models import ClientOptions, PreRequest

client_options = ClientOptions()
request_options = PreRequest("GET", "/")

class CompositionError(Exception): pass

class Composer:
    @staticmethod
    def consume_request(request: PreRequest, /) -> None:
        raise CompositionError("Request composition not supported")
    
def compose(obj, *composers):
    raise NotImplementedError

@dataclass
class HeaderComposer(Composer):
    key: str
    value: str

    def consume_request(self, request: PreRequest, /) -> None:
        request.headers[self.key] = self.value

compose(
    request_options,
    HeaderComposer("referer", "https://www.google.com/"),
    HeaderComposer("accept", "application/json"),
)

def make_consumer(referer: str, /):
    def consumer(request: PreRequest, /) -> None:
        request.headers["referer"] = referer

    return consumer

# A "request consumer"
def my_request_consumer(request: PreRequest, /) -> None:
    request.headers["referer"] = "https://www.google.com/"

# Similar to pydantic's WrapValidator etc.
RequestConsumer(my_request_consumer)
ClientConsumer(my_client_consumer)

# @dataclass
# class RefererHeaderConsumer(RequestConsumer):
#     referer: str

#     def consume_request(self, request: PreRequest, /):
#         request.headers["referer"] = self.referer


@with_referer("google.com")
@get("/ip")
def ip(): ...