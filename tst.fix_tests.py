from typing import Protocol, Optional
from fastclient import get, FastClient, Query

client: FastClient = FastClient("https://httpbin.org/")


class Service(Protocol):
    @get("/get")
    def get(self, q: Optional[str] = Query(default=None, required=False)):
        ...


@client.get("/get")
def get2(q: Optional[str] = Query(default=None, required=False)):
    ...


service: Service = client.create(Service)  # type: ignore

d = service.get()
# d2 = get2()