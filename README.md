# fastclient
:rocket: Fast API clients for Python inspired by [FastAPI](https://github.com/tiangolo/fastapi) and [Retrofit](https://square.github.io/retrofit/)

## Installation
```console
pip install git+https://github.com/tombulled/fastclient.git@main
```

## Getting Started
The simplest FastClient file could look like this:
```python
from fastclient import FastClient

app = FastClient("https://httpbin.org/")


@app.get("/ip")
def ip():
    ...
```
```python
>>> ip()
{'origin': '1.2.3.4'}
```

## User Guide
### Path Parameters
You can declare path "parameters" or "variables" with the same syntax used by Python format strings:
```python
from fastclient import FastClient

app = FastClient("https://jsonplaceholder.typicode.com/")


@app.get("/posts/{post_id}")
def get_post(post_id):
    ...
```
```python
>>> get_post(1)
{
    'userId': 1,
    'id': 1,
    'title': 'sunt aut facere repellat provident occaecati excepturi optio reprehenderit',
    'body': 'quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto'
}
```

#### Path parameters with types
You can declare the type of a path parameter in the function, using standard Python type annotations:
```python
from fastclient import FastClient

app = FastClient("https://jsonplaceholder.typicode.com/")


@app.get("/posts/{post_id}")
def get_post(post_id: int):
    ...
```
In this case, `item_id` is declared to be an `int`.

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