from dataclasses import dataclass

from neoclient import Service, base_url, get


@dataclass
class Response:
    args: dict
    headers: dict
    origin: str
    url: str


@base_url("https://httpbin.org/")
class Httpbin(Service):
    @get("/get")
    def get(self, message: str) -> Response: ...


httpbin: Httpbin = Httpbin()

response: Response = httpbin.get("Hello, World!")

print(response)
