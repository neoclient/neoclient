from typing import Mapping

from neoclient import NeoClient, QueryParams

client: NeoClient = NeoClient("http://127.0.0.1:8000/")


@client.get("/echo")
def echo(params: Mapping[str, str] = QueryParams()) -> Mapping[str, str]: ...
