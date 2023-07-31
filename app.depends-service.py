from neoclient import Headers, Service, get, service

def common_headers(headers=Headers()) -> None:
    headers.update({"x-client-name": "CLIENT-A", "x-client-version": "1.0.3"})

@service("https://httpbin.org/", dependencies=(common_headers,))
class Httpbin(Service):
    @get("/headers")
    def foo(self):
        ...

    @get("/headers")
    def bar(self):
        ...


httpbin = Httpbin()
