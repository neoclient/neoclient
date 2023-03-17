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
        'User-Agent': 'neoclient/0.1.22'
    },
    'origin': '1.2.3.4',
    'url': 'https://httpbin.org/get?message=Hello%2C+World!'
}
```