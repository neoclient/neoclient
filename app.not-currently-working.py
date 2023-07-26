from typing import MutableMapping
from neoclient import NeoClient
from neoclient.decorators import depends
from neoclient.param_functions import Header, Headers

client = NeoClient("https://httpbin.org/")


def token_length(
    headers: MutableMapping[str, str] = Headers(), x_token: str = Header()
) -> None:
    headers["X-Token-Length"] = str(len(x_token))


@depends(token_length)
@client.get("/get")
def request(x_token: str = Header()):
    ...
