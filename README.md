# neoclient
🚀 Fast API Clients for Python

## Installation
```console
pip install neoclient
```

## Introduction
The simplest `neoclient` file looks like this:
```python
from neoclient import get

@get("https://httpbin.org/ip")
def ip(): ...
```
```python
>>> ip()
{'origin': '1.2.3.4'}
```

If you've come from `requests` or `httpx`, the above example is equivelant to:
```python
from requests import get
# or: from httpx import get

def ip():
    return get("https://httpbin.org/ip").json()
```

### Client
Operations can share configuration from a `NeoClient` instance:
```python
from neoclient import NeoClient

client = NeoClient("https://httpbin.org/")

@client.get("/ip")
def ip(): ...
```
```python
>>> ip()
{'origin': '1.2.3.4'}
```