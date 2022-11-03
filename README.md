# fastclient
:rocket: Fast API Clients for Python

## Installation
```console
pip install git+https://github.com/tombulled/fastclient.git@main
```

## Documentation
### Introduction
The simplest `fastclient` file could look like this:
```python
from fastclient import get

@get("https://httpbin.org/ip")
def ip():
    ...
```
```python
>>> ip()
{'origin': '1.2.3.4'}
```

However, it's almost always better to create a `FastClient` instance for easy reusability:
```python
from fastclient import FastClient

client = FastClient("https://httpbin.org/")

@client.get("/ip")
def ip():
    ...
```
```python
>>> ip()
{'origin': '1.2.3.4'}
```

### Path Parameters
You can declare path parameters with the same syntax used by Python format strings:
```python
from fastclient import FastClient

client = FastClient("https://httpbin.org/")

@client.get("/base64/{value}")
def b64decode(value):
    ...
```
```python
>>> b64decode("RmFzdENsaWVudCBpcyBhd2Vzb21lIQ==")
'FastClient is awesome!'
```

#### Path parameters with types
You can declare the type of a path parameter in the function using standard Python type annotations:
```python
from fastclient import FastClient

client = FastClient("https://httpbin.org/")

@client.get("/base64/{value}")
def b64decode(value: str):
    ...
```
In this case, `value` is declared to be of type `str`.

#### Explicit path parameters
If you prefer explicitly stating that a parameter is a path parameter, you can use the `Path` parameter function:
```python
from fastclient import FastClient, Path

client = FastClient("https://httpbin.org/")

@client.get("/base64/{value}")
def b64decode(value: str = Path()):
    ...
```
This approach comes with added benefits, such as being able to specify a `default` value:
```python
from fastclient import FastClient, Path

client = FastClient("https://httpbin.org/")

@client.get("/base64/{value}")
def b64decode(value: str = Path(default="SGVsbG8sIFdvcmxkIQ==")):
    ...
```
```python
>>> b64decode()
'Hello, World!'
```

#### Missing path parameters
FastClient will throw an error if you specify a path parameter in the request path, however do not create a function parameter for it. For example:
```python
from fastclient import FastClient

client = FastClient("https://httpbin.org/")

@client.get("/base64/{value}")
def b64decode():
    ...
```
```python
>>> b64decode()
IncompatiblePathParameters: Expected ('value',), got ()
```

#### Pre-defined Values
If you have a path operation that receives a path parameter, but you want the possible valid path parameter values to be predefined, you can use a standard Python Enum.
```python
from enum import Enum
from fastclient import FastClient

class Name(str, Enum):
    def __str__(self):
        return self.value
        
    BOB = "bob"
    SALLY = "sally"

client = FastClient("https://httpbin.org/")

@client.get("/anything/{name}")
def anything(name: Name):
    ...
```
```python
>>> anything(Name.BOB)
{
    'args': {},
    'data': '',
    'files': {},
    'form': {},
    'headers': {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': 'httpbin.org',
        'User-Agent': 'fastclient/0.1.0'
    },
    'json': None,
    'method': 'GET',
    'origin': '1.2.3.4',
    'url': 'https://httpbin.org/anything/bob'
}
```

#### Path parameters containing paths
Let's say you have a path operation with a path `/do/{commands}`, where you expect `commands` to accept an arbitrary number of arguments which should be used as path segments. To achieve this, you can pass the path parameter a sequence:
```python
from typing import Sequence
from fastclient import FastClient

client = FastClient("https://httpbin.org/")

@client.get("/anything/{commands}")
def do(commands: Sequence[str]):
    ...
```
```python
>>> do(["turn", "left", "then", "turn", "right"])
{
    'args': {},
    'data': '',
    'files': {},
    'form': {},
    'headers': {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': 'httpbin.org',
        'User-Agent': 'fastclient/0.1.0'
    },
    'json': None,
    'method': 'GET',
    'origin': '1.2.3.4',
    'url': 'https://httpbin.org/anything/turn/left/then/turn/right'
}
```

### Query Parameters
When you declare other function parameters that are not part of the path parameters, they are automatically interpreted as "query" parameters.
```python
from fastclient import FastClient

app = FastClient("https://httpbin.org/")

@app.get("/get")
def get(message: str):
    ...
```
```python
>>> get("Hello, World!")
{
    'args': {'message': 'Hello, World!'},
    'headers': {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': 'httpbin.org',
        'User-Agent': 'python-httpx/0.23.0',
    },
    'origin': '1.2.3.4',
    'url': 'https://httpbin.org/get?message=Hello%2C+World!'
}
```

## Advanced User Guide
FastClient can turn your HTTP API into a Python protocol.
```python
from fastclient import FastClient, get
from typing import Protocol

class Httpbin(Protocol):
    @get("/get")
    def get(self, message: str) -> dict:
        ...

httpbin: Httpbin = FastClient("https://httpbin.org/").create(Httpbin)  # type: ignore
```
```python
>>> httpbin.get("Hello, World!")
{
    'args': {'message': 'Hello, World!'},
    'headers': {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': 'httpbin.org',
        'User-Agent': 'python-httpx/0.23.0',
        'X-Amzn-Trace-Id': 'Root=1-62fce22e-198b71ee738e804f05e7824f'
    },
    'origin': '1.2.3.4',
    'url': 'https://httpbin.org/get?message=Hello%2C+World!'
}
```