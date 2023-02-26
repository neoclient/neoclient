# State
Both `Request` and `Response` instances are capable of storing state. This can be
really powerful when used in conjunction with middleware.

## Request State
You can declare "state" parameters by using the `State` parameter function.
```python
from neoclient import NeoClient, State

client = NeoClient("https://httpbin.org/")


@client.get("/get")
def get(name: str = State()):
    ...
```
```python
>>> get("Jim Bob")
{
    'args': {},
    'headers': {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': 'httpbin.org',
        'User-Agent': 'neoclient/0.1.18'
    },
    'origin': '1.2.3.4',
    'url': 'https://httpbin.org/get'
}
```
State values are completely excluded from the request sent to the HTTP server,
therefore they are only of use to anything that interacts with the request
before it is sent - for example, middleware.

### Modifying Request State
Request state can be modified by using the `State` parameter, or through middleware.
```python
from neoclient import NeoClient, Request, Response, middleware
from neoclient.typing import CallNext

client = NeoClient("https://httpbin.org/")


def inspect_state(call_next: CallNext, request: Request) -> Response:
    print("Request State:", request.state)

    return call_next(request)


def some_middleware(call_next: CallNext, request: Request) -> Response:
    request.state.message = "Hello, World!"

    return call_next(request)


@middleware(inspect_state, some_middleware)
@client.get("/status/200")
def request() -> None:
    ...
```
```python
>>> request()
Request State: State(message='Hello, World!')
```

### Using Request State
Request state should be used when a parameter's value needs to be used multiple
times.
```python
from neoclient import NeoClient, Request, Response, State, middleware
from neoclient.typing import CallNext

client = NeoClient("https://httpbin.org/")


def add_message_headers(call_next: CallNext, request: Request) -> Response:
    name: str = request.state.name

    request.headers["X-Name-Lower"] = name.lower()
    request.headers["X-Name-Title"] = name.title()
    request.headers["X-Name-Upper"] = name.upper()

    return call_next(request)


@middleware(add_message_headers)
@client.get("/headers")
def request(name: str = State()):
    ...
```
```python
>>> request("Ada Lovelace")
{
    'headers': {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': 'httpbin.org',
        'User-Agent': 'neoclient/0.1.18',
        'X-Name-Lower': 'ada lovelace',
        'X-Name-Title': 'Ada Lovelace',
        'X-Name-Upper': 'ADA LOVELACE'
    }
}
```

## Response State
Like requests, responses can also contain state.
```python
from neoclient import NeoClient, Request, Response, State, middleware
from neoclient.typing import CallNext

client = NeoClient("https://httpbin.org/")


def response(message: str = State()) -> str:
    return message


def some_middleware(call_next: CallNext, request: Request) -> Response:
    response: Response = call_next(request)

    response.state.message = "Hello, World!"

    return response


@middleware(some_middleware)
@client.get("/status/200", response=response)
def request() -> str:
    ...
```
```python
>>> request()
'Hello, World!'
```
In the above example, `some_middleware` adds a `message` to the response state,
which the `response` function then extracts from the response state and returns.