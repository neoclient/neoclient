from dataclasses import dataclass

from neoclient.composers import Composer, QueryComposer, compose
from neoclient.models import ClientOptions, PreRequest

"""
from neoclient.models import PreRequest
from neoclient.composers import HeaderComposer
from neoclient.TODO import compose

request = PreRequest("GET", "/")

compose(request, HeaderComposer("referer", "https://www.google.com/"))
"""

# @dataclass
# class HeaderComposer(Composer):
#     key: str
#     value: str

#     def compose_request(self, request: PreRequest, /) -> None:
#         request.headers[self.key] = self.value

client_options = ClientOptions()
request_options = PreRequest("GET", "/")

compose(
    request_options,
    # HeaderComposer("referer", "https://www.google.com/"),
    # HeaderComposer("accept", "application/json"),
    QueryComposer("name", "sam"),
    QueryComposer("age", 10),
)
