from typing import Mapping

from neoclient import FastClient, Headers

client: FastClient = FastClient(base_url="http://127.0.0.1:8000/")


@client.get("/echo")
def echo(headers: Mapping[str, str] = Headers()) -> Mapping[str, str]:
    ...
