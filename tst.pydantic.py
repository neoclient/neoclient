from httpx import QueryParams
import pydantic
from neoclient.models import RequestOpts


class BaseModel(pydantic.BaseModel):
    # model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)
    class Config:
        arbitrary_types_allowed = True


class Model(BaseModel):
    # params: QueryParams
    request: RequestOpts


# m = Model(params=QueryParams({"name": "sam"}))
m = Model(request=RequestOpts("GET", "/"))
