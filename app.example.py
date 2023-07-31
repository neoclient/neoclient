from neoclient import NeoClient
from neoclient.decorators import depends
from neoclient.param_functions import Req

client = NeoClient("https://httpbin.org/")


def some_dependency(request=Req()) -> None:
    request.headers["x-foo"] = "bar"


@depends(some_dependency)
@client.get("/get")
def request():
    ...
