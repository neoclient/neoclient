from retrofit import Retrofit, get, post, HeaderDict, Header, Query, Path, QueryDict, Body
from retrofit.converters import IdentityConverter, IdentityResolver
from typing import Any, Dict, List, Protocol, Optional, Set


class HttpBinService(Protocol):
    ### Request Inspection
    @get
    def ip() -> dict:
        ...

    @get
    def headers(headers: dict = HeaderDict(default_factory=dict)) -> dict:
        ...

    @get
    def user_agent(user_agent: str = Header()) -> dict:
        ...

    @get
    def redirect_to(
        url: str = Query(), status_code: Optional[int] = Query(default=None)
    ) -> dict:
        ...

    @get("status/{code}")
    def status(code: int = Path()) -> dict:
        ...

    @get
    def get(params: dict = QueryDict(default_factory=dict)) -> dict:
        ...

    @post
    def post(message: str = Body()) -> dict:
        ...


retrofit: Retrofit = Retrofit(
    base_url="https://httpbin.org/",
    resolver=IdentityResolver(),
    converter=IdentityConverter(),
)

httpbin: HttpBinService = retrofit.create(HttpBinService)
