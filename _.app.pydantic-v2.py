from typing import Mapping
from pydantic import BaseModel, ConfigDict


class Request(BaseModel):
    model_config = ConfigDict(strict=True)

    path_params: Mapping[str, str]


path_params: Mapping[str, str] = {"name": "sam", "age": "43"}

r: Request = Request(path_params=path_params)
