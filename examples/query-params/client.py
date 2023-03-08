from typing import Mapping

from neoclient import NeoClient, Queries

client: NeoClient = NeoClient("http://127.0.0.1:8000/")


@client.get("/echo")
def echo(params: Mapping[str, str] = Queries()) -> Mapping[str, str]:
    ...
