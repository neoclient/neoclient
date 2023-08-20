from neoclient import NeoClient
from neoclient.decorators import request_depends
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


@request_depends(common_headers)
@client.get("/get")
def request():
    ...