from dataclasses import dataclass
from typing import Mapping
from pydantic import BaseConfig, BaseModel, create_model
from pydantic.main import ModelMetaclass


class Request(BaseModel):
    class Config:
        copy_on_model_validation: str = "none"
        # copy_on_model_validation = False

    path_params: Mapping[str, str]


@dataclass
class Request2:
    path_params: Mapping[str, str]


path_params: Mapping[str, str] = {"name": "sam", "age": "43"}

r: Request = Request(path_params=path_params)
r2: Request2 = Request2(path_params=path_params)


class Request3Config(BaseConfig):
    copy_on_model_validation = "none"


class Request3BaseModel(BaseModel):
    Config = Request3Config


# Request3 = create_model(
#     "Request3", path_params=(Mapping[str, str], ...), __base__=Request3BaseModel, __module__="foo"
# )
Request3 = create_model(
    "Request3",
    path_params=(Mapping[str, str], ...),
    __config__=Request3Config,
    __module__="foo",
)

r3: Request3 = Request3(path_params=path_params)

from fastapi.utils import create_response_field

r4 = create_response_field(
    "path_params", Mapping[str, str], model_config=Request3Config
)

r4_pp = r4.validate(path_params, {}, loc="loc")[0]


class Request5BaseModel(BaseModel):
    Config = Request3Config

    path_params: Mapping[str, str]


r5 = ModelMetaclass.__new__(ModelMetaclass, "R5", (Request5BaseModel,), {})


class PathParams(BaseModel):
    __root__ = Mapping[str, str]


class Request6(BaseModel):
    path_params: PathParams


r6 = Request6(path_params=path_params)
r6_pp = r6.path_params
