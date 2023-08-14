from typing import Mapping

from neoclient import NeoClient, PathParams

client: NeoClient = NeoClient("http://127.0.0.1:8000/")


@client.get("/{action}/{item}/{time}")
def perform(path_params: Mapping[str, str] = PathParams()) -> Mapping[str, str]:
    ...
