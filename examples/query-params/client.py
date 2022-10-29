from typing import Mapping
from fastclient import FastClient, QueryParams

client: FastClient = FastClient(base_url="http://127.0.0.1:8000/")


@client.get("/echo")
def echo(params: Mapping[str, str] = QueryParams()) -> Mapping[str, str]:
    ...
