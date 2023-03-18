# Path Parameter
You can declare path parameters with the same syntax used by Python format strings:
```python
from neoclient import NeoClient

client = NeoClient("https://httpbin.org/")

@client.get("/base64/{value}")
def b64decode(value):
    ...
```
```python
>>> b64decode("RmFzdENsaWVudCBpcyBhd2Vzb21lIQ==")
'NeoClient is awesome!'
```

## Path parameters with types
You can declare the type of a path parameter in the function using standard Python type annotations:
```python
from neoclient import NeoClient

client = NeoClient("https://httpbin.org/")

@client.get("/base64/{value}")
def b64decode(value: str):
    ...
```
In this case, `value` is declared to be of type `str`.

## Explicit path parameters
If you prefer explicitly stating that a parameter is a path parameter, you can use the `Path` parameter function:
```python
from neoclient import NeoClient, Path

client = NeoClient("https://httpbin.org/")

@client.get("/base64/{value}")
def b64decode(value: str = Path()):
    ...
```
This approach comes with added benefits, such as being able to specify validation constraints.
```python
from neoclient import NeoClient, Path

client = NeoClient("https://httpbin.org/")

@client.get("/base64/{value}")
def b64decode(value: str = Path(default="SGVsbG8sIFdvcmxkIQ==")):
    ...
```
```python
>>> b64decode()
'Hello, World!'
```

## Missing path parameters
NeoClient will throw an error if you specify a path parameter in the request path, however do not create a function parameter for it. For example:
```python
from neoclient import NeoClient

client = NeoClient("https://httpbin.org/")

@client.get("/base64/{value}")
def b64decode():
    ...
```
```python
>>> b64decode()
IncompatiblePathParameters: Expected ('value',), got ()
```

## Pre-defined Values
If you have a path operation that receives a path parameter, but you want the possible valid path parameter values to be predefined, you can use a standard Python Enum.
```python
from enum import Enum
from neoclient import NeoClient

class Name(str, Enum):
    def __str__(self):
        return self.value
        
    BOB = "bob"
    SALLY = "sally"

client = NeoClient("https://httpbin.org/")

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
        'User-Agent': 'neoclient/0.1.25'
    },
    'json': None,
    'method': 'GET',
    'origin': '1.2.3.4',
    'url': 'https://httpbin.org/anything/bob'
}
```

## Path parameters containing paths
Let's say you have a path operation with a path `/do/{commands}`, where you expect `commands` to accept an arbitrary number of arguments which should be used as path segments. To achieve this, you can pass the path parameter a sequence:
```python
from typing import Sequence
from neoclient import NeoClient

client = NeoClient("https://httpbin.org/")

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
        'User-Agent': 'neoclient/0.1.25'
    },
    'json': None,
    'method': 'GET',
    'origin': '1.2.3.4',
    'url': 'https://httpbin.org/anything/turn/left/then/turn/right'
}
```