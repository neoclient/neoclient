from .params import Param
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Union
import httpx
from httpx import URL, QueryParams, Headers, Cookies, Timeout
from .types import HeadersType, TimeoutType, MethodType, UrlType, ParamsType, JsonType, CookiesType, TimeoutType


class Request:
    _method: str
    _url: URL
    _params: QueryParams
    _headers: Headers
    _json: Any
    _cookies: Cookies
    _timeout: Timeout

    def __init__(
        self,
        method: MethodType,
        url: UrlType,
        *,
        params: ParamsType = None,
        headers: HeadersType = None,
        cookies: CookiesType = None,
        json: JsonType = None,
        timeout: TimeoutType = Timeout(5.0),
    ) -> None:
        self.method = method if isinstance(method, str) else method.decode()
        self.url = URL(url)
        self.params = QueryParams(params)
        self.headers = Headers(headers)
        self.json = json
        self.cookies = Cookies(cookies)
        self.timeout = Timeout(timeout)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(method={self.method!r}, url={self.url!r}, params={self.params!r}, headers={self.headers!r}, cookies={self.cookies!r}, json={self.json!r}, timeout={self.timeout!r})"

    @property
    def method(self) -> str:
        return self._method

    @method.setter
    def method(self, value: MethodType, /) -> None:
        self._method = value if isinstance(value, str) else value.decode()

    @property
    def url(self) -> URL:
        return self._url

    @url.setter
    def url(self, value: UrlType, /) -> None:
        self._url = URL(value)

    @property
    def params(self) -> QueryParams:
        return self._params

    @params.setter
    def params(self, value: ParamsType, /) -> None:
        self._params = QueryParams(value)

    @property
    def headers(self) -> Headers:
        return self._headers

    @headers.setter
    def headers(self, value: HeadersType, /) -> None:
        self._headers = Headers(value)

    @property
    def json(self) -> Any:
        return self._json

    @json.setter
    def json(self, value: JsonType, /) -> None:
        self._json = value

    @property
    def cookies(self) -> Cookies:
        return self._cookies

    @cookies.setter
    def cookies(self, value: CookiesType, /) -> None:
        self._cookies = Cookies(value)

    @property
    def timeout(self) -> Timeout:
        return self._timeout

    @timeout.setter
    def timeout(self, value: TimeoutType, /) -> None:
        self._timeout = Timeout(value)

@dataclass
class ClientConfig:
    base_url: Union[httpx.URL, str] = ""
    headers: HeadersType = None
    timeout: TimeoutType = None

    def build(self) -> httpx.Client:
        return httpx.Client(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
        )

    def is_default(self) -> bool:
        return all(
            (
                self.headers == None,
                self.base_url == "",
                self.timeout == None,
            )
        )

    @classmethod
    def from_client(cls, client: httpx.Client, /) -> "ClientConfig":
        return cls(
            base_url=client.base_url,
            headers=client.headers,
            timeout=client.timeout,
        )


@dataclass
class Specification:
    request: Request
    response: Optional[Callable[..., Any]] = None
    params: Dict[str, Param] = field(default_factory=dict)
