from typing import MutableMapping

from neoclient import PathParams, get, request_depends


def add_path_params(path_params: MutableMapping[str, str] = PathParams()) -> None:
    path_params.update({"endpoint": "get"})


@request_depends(add_path_params)
@get("http://127.0.0.1:8080/{endpoint}")
def request():
    ...
