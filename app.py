from retrofit import (
    Retrofit,
    get,
    post,
    Headers,
    Header,
    Query,
    Path,
    Queries,
    # Body,
    headers,
    query_params,
    Cookie,
    Cookies,
    Body,
)
from retrofit.converters import IdentityConverter, IdentityResolver
from typing import Any, Dict, List, Protocol, Optional, Set
from pydantic import BaseModel
from retrofit.models import Request

class Model(BaseModel):
    id: int
    name: str

class User(Model): pass
class Item(Model): pass


class HttpBinService(Protocol):
    ## Request Inspection
    # @get("ip")
    # def ip(self) -> dict:
    #     ...

    # @get("headers")
    # def headers(self, headers: dict = Headers(default_factory=lambda: {"x-foo": "bar"})) -> dict:
    #     ...

    # @get("user-agent")
    # def user_agent(self, user_agent: str = Header()) -> dict:
    #     ...

    # @get
    # def redirect_to(
    #     url: str = Query(), status_code: Optional[int] = Query(default=None)
    # ) -> dict:
    #     ...

    # @get("status/{code}")
    # def status(self, code: int) -> dict:
    #     ...

    # @get("get")
    # def get(self, q: Optional[str] = Query(default=None)) -> dict:
    #     ...

    # @get("/users/{id}")
    # def get_user(self, id: str = Path("id")) -> dict:
    #     ...

    @post("/users/")
    def create_user(self, user: User, item: Item) -> Request:
        ...

    # @headers({"User-Agent": "robototron", "X-Who-Am-I": "Sam"})
    # @query_params({"foo": "bar", "cat": "dog"})
    # @post
    # def post(message: str = Body()) -> dict:
    #     ...

    # @get("cookies")
    # def cookies(self, cookies: dict = Cookies()):
    #     ...


retrofit: Retrofit = Retrofit(
    base_url="https://httpbin.org/",
    resolver=IdentityResolver(),
    converter=IdentityConverter(),
)

httpbin: HttpBinService = retrofit.create(HttpBinService)  # type: ignore

req: Request = httpbin.create_user(User(id=1, name="User"), Item(id=1, name="Item"))