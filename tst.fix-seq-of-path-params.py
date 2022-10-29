from typing import Sequence
from fastclient import FastClient, Path

client: FastClient = FastClient(base_url="http://127.0.0.1:8000/")


@client.get("/{other}/{path_params}")
def echo(other: str = Path(), path_params: Sequence[str] = Path()) -> Sequence[str]:
    ...


print(echo("shout", ["i", "like", "fish", "and", "chips"]))
