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
