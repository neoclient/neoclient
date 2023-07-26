# Request Dependencies
When parts of your request depend upon other parts of your request, you can use
request dependencies. Request dependencies can also come in handy if you need
to add the same information to multiple requests.

For example, assume you have an authentication operation that needs to send
off a `token`, however it also needs to declare the length of the token.

```python
from neoclient import NeoClient
from neoclient.decorators import depends
from neoclient.param_functions import Header
from neoclient.models import Request

client = NeoClient("https://httpbin.org/")


def token_length(request: Request) -> None:
    request.headers["X-Token-Length"] = str(len(request.headers["X-Token"]))


@depends(token_length)
@client.get("/get")
def request(x_token: str = Header()):
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
from neoclient.models import Request

client = NeoClient("https://httpbin.org/")


def common_headers(request: Request) -> None:
    request.headers.update(
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
