from neoclient import Service, get
from neoclient.decorators import service


@service(base_url="https://httpbin.org/")
class Httpbin(Service):
    @service.response
    def _response(self, body: dict) -> str:
        return body["origin"]

    @get("/ip")
    def ip(self):
        ...


httpbin = Httpbin()
