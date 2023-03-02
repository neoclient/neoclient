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