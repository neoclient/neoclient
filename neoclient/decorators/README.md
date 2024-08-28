# neoclient/decorators
NeoClient Decorators

## About
These decorators allow you to configure your operations and services.

## Available Decorators
### Headers
#### `accept`
Set an `Accept` header on the request
```python
from neoclient import get
from neoclient.decorators import accept


@accept("application/json")
@get("https://httpbin.org/ip")
def ip(): ...
```

The above is equivelant to:
```python
from httpx import get

def ip():
    return get("https://httpbin.org/ip", headers={"accept": "application/json"})
```