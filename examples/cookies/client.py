from typing import Mapping

from fastclient import Cookies, FastClient

client: FastClient = FastClient(base_url="http://127.0.0.1:8000/")


@client.get("/echo")
def echo(cookies: Mapping[str, str] = Cookies()) -> Mapping[str, str]:
    ...
