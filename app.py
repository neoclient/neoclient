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
)
from retrofit.converters import IdentityConverter, IdentityResolver
from typing import Any, Dict, List, Protocol, Optional, Set


class HttpBinService(Protocol):
    ## Request Inspection
    @get("ip")
    def ip() -> dict:
        ...

    @get("headers")
    def headers(headers: dict = Headers()) -> dict:
        ...

    # @get
    # def user_agent(user_agent: str = Header()) -> dict:
    #     ...

    # @get
    # def redirect_to(
    #     url: str = Query(), status_code: Optional[int] = Query(default=None)
    # ) -> dict:
    #     ...

    # @get("status/{code}")
    # def status(code: int = Path()) -> dict:
    #     ...

    # @get
    # def get(params: dict = QueryDict(default_factory=dict)) -> dict:
    #     ...

    # @headers({"User-Agent": "robototron", "X-Who-Am-I": "Sam"})
    # @query_params({"foo": "bar", "cat": "dog"})
    # @post
    # def post(message: str = Body()) -> dict:
    #     ...


retrofit: Retrofit = Retrofit(
    base_url="https://httpbin.org/",
    resolver=IdentityResolver(),
    converter=IdentityConverter(),
)

httpbin: HttpBinService = retrofit.create(HttpBinService)
