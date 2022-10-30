from typing import Mapping

from fastclient import FastClient, Paths

client: FastClient = FastClient(base_url="http://127.0.0.1:8000/")


@client.get("/{action}/{item}/{time}")
def perform(path_params: Mapping[str, str] = Paths()) -> Mapping[str, str]:
    ...
