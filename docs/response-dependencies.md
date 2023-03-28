# Response Dependencies
When you would like to extract information from a response in a similar way for
multiple different operations, you can use response dependencies.
```python
from neoclient import Depends, NeoClient
from neoclient.dependencies import status_code, reason_phrase

client = NeoClient("https://httpbin.org/")


def response(
    status_code: int = Depends(status_code),
    reason_phrase: str = Depends(reason_phrase),
) -> str:
    return f"{status_code} {reason_phrase}"


@client.get("/get", response=response)
def request():
    ...

```
```python
>>> request()
'200 OK'
```

## Define your own response dependencies
To define your own response dependencies, simply create a callable that accepts
an available aspect of the response, and returns what you desire:
```python
from neoclient import Depends, NeoClient, Response

client = NeoClient("https://httpbin.org/")


def server(response: Response) -> str:
    return response.headers["server"].split("/")[0]


def response(server: str = Depends(server)) -> str:
    return server


@client.get("/get", response=response)
def request():
    ...
```
```python
>>> request()
'gunicorn'
```
The above example could be simplied futher down to just:
```python
from neoclient import Header, NeoClient

client = NeoClient("https://httpbin.org/")


def server_name(server: str = Header()) -> str:
    return server.split("/")[0]


@client.get("/get", response=server_name)
def request():
    ...
```
```python
>>> request()
'gunicorn'
```