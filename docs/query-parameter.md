# Query Parameter
When you declare other function parameters that are not part of the path parameters, they are automatically interpreted as "query" parameters.
```python
from neoclient import NeoClient

client = NeoClient("https://httpbin.org/")

@client.get("/get")
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
        'User-Agent': 'neoclient/0.1.28'
    },
    'origin': '1.2.3.4',
    'url': 'https://httpbin.org/get?message=Hello%2C+World!'
}
```

## Multi-Value Query Parameters
In order to repeat query parameters, e.g. `?name=sam&name=bob`, use type annotations
to indicate that the value is a list.
```python
from typing import List
from neoclient import NeoClient

client = NeoClient("https://httpbin.org/")

@client.get("/get")
def get(name: List[str]):
    ...
```
```python
>>> get(["sam", "bob"])
{
    'args': {'name': ['sam', 'bob']},
    'headers': {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': 'httpbin.org',
        'User-Agent': 'neoclient/0.1.28'
    },
    'origin': '1.2.3.4',
    'url': 'https://httpbin.org/get?name=sam&name=bob'
}
```