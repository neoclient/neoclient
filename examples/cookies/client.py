from typing import Mapping

from neoclient import Cookies, NeoClient

client: NeoClient = NeoClient("http://127.0.0.1:8000/")


@client.get("/echo")
def echo(cookies: Mapping[str, str] = Cookies()) -> Mapping[str, str]:
    ...
