# Consumers

## Theory

Consumers are operations that accept a single input argument and return no result.

For reference, the `neoclient.typing.Consumer` protocol (interface) looks like this:

```python
class Consumer(Protocol[T_contra]):
    def __call__(self, t: T_contra, /) -> None:
        ...
```

If you're familiar with Java, this will likely remind you of [`java.util.function.Consumer`](https://docs.oracle.com/javase/8/docs/api/java/util/function/Consumer.html).

Below is an example of a simple string consumer (a `Consumer[str]`):

```python
def greet(name: str, /) -> None:
    print("Hello", name)
```

## First Principles

With regard to `neoclient`, consumers are used to configure/modify objects such as requests.

For example, imagine we have a simple `Request` model such as:

```python
from dataclasses import dataclass, field
from typing import Mapping

@dataclass
class Request:
    method: str
    url: str
    headers: Mapping[str, str] = field(default_factory=dict)
```

We could then define a consumer to modify an aspect of a request, for example:

```python
def add_referer(request: Request, /) -> None:
    request.headers["referer"] = "https://www.google.com/"
```

Then we could use it like:

```python
>>> request = Request("GET", "/foo")
>>> request
Request(method='GET', url='/foo', headers={})
>>> add_referer(request)
>>> request
Request(method='GET', url='/foo', headers={'referer': 'https://www.google.com/'})
```

## Available Consumers

`neoclient` provides a set of handy consumers out of the box. For example, to replicate our above example:

```python
from neoclient.consumers import HeaderConsumer

add_referer = HeaderConsumer("referer", "https://www.google.com/")
```

Then we can use the consumer like this:

```python
from neoclient import PreRequest

request = PreRequest("GET", "/")

add_referer.consume_request(request)

assert request.headers == {"referer": "https://www.google.com/"}
```
