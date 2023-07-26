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
