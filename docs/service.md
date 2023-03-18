# Service Classes
Service classes allow you to group together related operations in a class.
```python
from neoclient import Service, base_url, get


@base_url("https://httpbin.org/")
class Httpbin(Service):
    @get("/ip")
    def ip(self):
        ...


httpbin = Httpbin()
```
```python
>>> httpbin.ip()
{'origin': '1.2.3.4'}
```

## Service Middleware
Service classes can have service-level middleware defined within the class:
```python
from neoclient import Service, base_url, get, service, Request, Response
from neoclient.typing import CallNext


@base_url("https://httpbin.org/")
class Httpbin(Service):
    @service.middleware
    def _log(self, call_next: CallNext, request: Request) -> Response:
        print("Request:", request)

        return call_next(request)

    @get("/ip")
    def ip(self):
        ...


httpbin = Httpbin()
```
```python
>>> httpbin.ip()
Request: <Request('GET', 'https://httpbin.org/ip')>
{'origin': '1.2.3.4'}
```

## Service Response
Service classes can define a service-level default response dependency within
the class:
```python
from neoclient import Service, base_url, get, service


@base_url("https://httpbin.org/")
class Httpbin(Service):
    @service.response
    def _response(self, body: dict) -> str:
        return body["origin"]

    @get("/ip")
    def ip(self) -> str:
        ...


httpbin = Httpbin()
```
```python
>>> httpbin.ip()
'1.2.3.4'
```