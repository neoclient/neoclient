from fastclient import get, FastClient
from typing import Protocol

class Httpbin(Protocol):
    @get("/ip")
    def ip(self):
        ...

class FakeHttpbin(Httpbin):
    ...

# httpbin: Httpbin = FastClient("https://httpbin.org/").create(Httpbin)