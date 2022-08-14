from retrofit import Retrofit, get, post, put, request
from retrofit.models import Path, Query, Header, HeaderDict, QueryDict
from typing import Any, Dict, Optional, Protocol

"""
TODO:
    Implement `Headers`, `QueryParams`
    Implement @Body, @Field etc.
    Switch to `furl` over `urllib.parse`
"""


class HttpBinService(Protocol):
    ### Request Inspection
    @get
    def ip(self) -> dict:
        ...

    @get
    def headers(self, headers: dict = HeaderDict(default_factory=dict)) -> dict:
        ...

    @get
    def user_agent(self, user_agent: str = Header()) -> dict:
        ...

    @get
    def redirect_to(
        self, url: str = Query(), status_code: Optional[int] = Query(default=None)
    ) -> dict:
        ...

    @get("status/{code}")
    def status(self, code: int = Path()) -> dict:
        ...

    @get
    def get(self, params: dict = QueryDict(default_factory=dict)) -> dict:
        ...


retrofit: Retrofit = Retrofit("https://httpbin.org/")

httpbin: HttpBinService = retrofit.create(HttpBinService)
