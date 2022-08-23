# fastclient
:rocket: Fast API clients for Python inspired by [FastAPI](https://github.com/tiangolo/fastapi) and [Retrofit](https://square.github.io/retrofit/)

## Installation
```console
pip install git+https://github.com/tombulled/fastclient.git@main
```

## Usage
```python
from fastclient import FastClient

app = FastClient("https://httpbin.org/")

@app.get("/ip")
def ip() -> dict:
    ...
```
```python
>>> ip()
{'origin': '1.2.3.4'}
```

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