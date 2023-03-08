from typing import Mapping
from neoclient import NeoClient, Request, Response
from neoclient.typing import CallNext

client: NeoClient = NeoClient("https://httpbin.org/")


@client.middleware
def log_request(call_next: CallNext, request: Request) -> Response:
    print("Request:", request)

    response: Response = call_next(request)

    print("Response:", response)

    return response


@client.get("/ip")
def get_ip() -> Mapping[str, str]:
    ...


ip: Mapping[str, str] = get_ip()

print(ip)
