# neoclient
🚀 Fast API Clients for Python

## Installation
```console
pip install neoclient
```

## Introduction
The simplest `neoclient` file might look like this:
```python
from neoclient import get

@get("https://httpbin.org/ip")
def ip():
    ...
```
```python
>>> ip()
{'origin': '1.2.3.4'}
```

However, it's almost always better to create a `NeoClient` instance:
```python
from neoclient import NeoClient

client = NeoClient("https://httpbin.org/")

@client.get("/ip")
def ip():
    ...
```
```python
>>> ip()
{'origin': '1.2.3.4'}
```