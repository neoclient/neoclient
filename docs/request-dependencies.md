# Request Dependencies
When parts of your request depend upon other parts of your request, you can use
request dependencies. Request dependencies can also come in handy if you need
to add the same information to multiple requests.

For example, assume you have an authentication operation that needs to send
off a `token`, however it also needs to declare the length of the token.

```python
from neoclient import NeoClient
from neoclient.decorators import depends
from neoclient.param_functions import Header, Headers

client = NeoClient("https://httpbin.org/")


def token_length(headers=Headers(), x_token=Header()) -> None:
    headers["X-Token-Length"] = str(len(x_token))


@depends(token_length)
@client.get("/get")
def request(x_token=Header()):
    ...

```
```python
>>> request("some-token")
{
    'args': {},
    'headers': {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': 'httpbin.org',
        'User-Agent': 'neoclient/0.1.27',
        'X-Token': 'some-token',
        'X-Token-Length': '10'
    },
    'origin': '1.2.3.4',
    'url': 'https://httpbin.org/get'
}

```

## Add common information to requests
If some of your operations require the same common information, this is a perfect
opportunity to use request dependencies.

```python
from neoclient import NeoClient
from neoclient.decorators import depends
from neoclient.param_functions import Headers

client = NeoClient("https://httpbin.org/")


def common_headers(headers=Headers()) -> None:
    headers.update(
        {
            "x-format": "json",
            "x-token": "abc123",
            "x-dnt": "true",
        }
    )


@depends(common_headers)
@client.get("/get")
def request():
    ...
```
```python
>>> request()
{
    'args': {},
    'headers': {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': 'httpbin.org',
        'User-Agent': 'neoclient/0.1.27',
        'X-Dnt': 'true',
        'X-Format': 'json',
        'X-Token': 'abc123'
    },
    'origin': '1.2.3.4',
    'url': 'https://httpbin.org/get'
}
```

## Chaining dependencies
It is possible to chain request dependencies together through the use of the
`Dependency(...)` parameter function.

```python
from neoclient import NeoClient
from neoclient.decorators import depends
from neoclient.param_functions import Depends, Header, Headers

client = NeoClient("https://httpbin.org/")


def token_length(x_token=Header()):
    return len(x_token)


def common_headers(headers=Headers(), x_token_length=Depends(token_length)) -> None:
    headers["X-Token-Length"] = str(x_token_length)


@depends(common_headers)
@client.get("/get")
def request(x_token=Header()):
    ...
```
```python
>>> request("some-token")
{
    'args': {},
    'headers': {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': 'httpbin.org',
        'User-Agent': 'neoclient/0.1.27',
        'X-Token': 'some-token',
        'X-Token-Length': '10'
    },
    'origin': '1.2.3.4',
    'url': 'https://httpbin.org/get'
}
```

## Service-level dependencies
Request dependencies can be applied at the service-level using the `@depends`
decorator.

```python
from neoclient import Headers, Service, base_url, depends, get


def common_headers(headers=Headers()) -> None:
    headers.update({"x-client-name": "CLIENT-A", "x-client-version": "1.0.3"})


@depends(common_headers)
@base_url("https://httpbin.org/")
class Httpbin(Service):
    @get("/headers")
    def foo(self):
        ...

    @get("/headers")
    def bar(self):
        ...

httpbin = Httpbin()
```
```python
>>> httpbin.foo()
{
    'headers': {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': 'httpbin.org',
        'User-Agent': 'python-httpx/0.23.3',
        'X-Client-Name': 'CLIENT-A',
        'X-Client-Version': '1.0.3'
    }
}
```

If you prefer, you can also specify service-level dependencies using the `@service`
decorator:
```python
from neoclient import Headers, Service, get, service

def common_headers(headers=Headers()) -> None:
    headers.update({"x-client-name": "CLIENT-A", "x-client-version": "1.0.3"})

@service("https://httpbin.org/", dependencies=(common_headers,))
class Httpbin(Service):
    @get("/headers")
    def foo(self):
        ...

    @get("/headers")
    def bar(self):
        ...


httpbin = Httpbin()
```
```python
>>> httpbin.foo()
{
    'headers': {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': 'httpbin.org',
        'User-Agent': 'python-httpx/0.23.3',
        'X-Client-Name': 'CLIENT-A',
        'X-Client-Version': '1.0.3'
    }
}
```

### Inline service-level dependencies
If you prefer, or if your needs necessitate, you can define request dependencies
inline in your service class. For example:

```python
from neoclient import Headers, Service, base_url, get, service


@base_url("https://httpbin.org/")
class Httpbin(Service):
    @service.depends
    def common_headers(self, headers=Headers()) -> None:
        headers.update({"x-client-name": "CLIENT-A", "x-client-version": "1.0.3"})

    @get("/headers")
    def foo(self):
        ...

    @get("/headers")
    def bar(self):
        ...


httpbin = Httpbin()
```
```python
>>> httpbin.foo()
{
    'headers': {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': 'httpbin.org',
        'User-Agent': 'python-httpx/0.23.3',
        'X-Client-Name': 'CLIENT-A',
        'X-Client-Version': '1.0.3'
    }
}
```

## Client-level dependencies
Request dependencies can be applied at the client-level using the client's `depends`
decorator.

```python
from neoclient import NeoClient, Headers

client = NeoClient("https://httpbin.org/")


@client.depends
def common_headers(headers=Headers()):
    headers["X-Token"] = "some-token-123"


@client.get("/headers")
def request():
    ...
```
```python
>>> request()
{
    'headers': {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': 'httpbin.org',
        'User-Agent': 'neoclient/0.1.27',
        'X-Token': 'some-token-123'
    }
}
```