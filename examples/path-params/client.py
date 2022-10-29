from typing import Sequence
from fastclient import FastClient, Path

client: FastClient = FastClient(base_url="http://127.0.0.1:8000/")


@client.get("/{path_params}")
def echo(path_params: Sequence[str] = Path()) -> Sequence[str]:
    ...
