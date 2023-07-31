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
