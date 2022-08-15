from retrofit import Retrofit, get, HeaderDict, Header, Query, Path, QueryDict
from retrofit.converters import HttpxResolver, HttpxJsonConverter
from typing import Protocol, Optional


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


retrofit: Retrofit = Retrofit(
    base_url="https://httpbin.org/",
    resolver=HttpxResolver(),
    converter=HttpxJsonConverter()
)

httpbin: HttpBinService = retrofit.create(HttpBinService)
