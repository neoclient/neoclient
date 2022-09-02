from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

import httpx
from httpx import URL, Cookies, Headers, QueryParams, Timeout
from httpx._config import DEFAULT_MAX_REDIRECTS, DEFAULT_TIMEOUT_CONFIG

from .params import Param
from .types import (
    AuthTypes,
    CookieTypes,
    DefaultEncodingTypes,
    EventHooks,
    HeaderTypes,
    JsonTypes,
    MethodTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestFiles,
    TimeoutTypes,
    URLTypes,
)


@dataclass(init=False)
class ClientOptions:
    auth: Optional[AuthTypes]
    params: QueryParams
    headers: Headers
    cookies: Cookies
    timeout: Timeout
    follow_redirects: bool
    max_redirects: int
    event_hooks: EventHooks
    base_url: URL
    trust_env: bool
    default_encoding: DefaultEncodingTypes

    def __init__(
        self,
        auth: Optional[AuthTypes] = None,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
        follow_redirects: bool = False,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        event_hooks: Optional[EventHooks] = None,
        base_url: URLTypes = "",
        trust_env: bool = True,
        default_encoding: DefaultEncodingTypes = "utf-8",
    ) -> None:
        self.auth = auth
        self.params = QueryParams(params)
        self.headers = Headers(headers)
        self.cookies = Cookies(cookies)
        self.timeout = Timeout(timeout)
        self.follow_redirects = follow_redirects
        self.max_redirects = max_redirects
        self.event_hooks = (
            event_hooks if event_hooks is not None else {"request": [], "response": []}
        )
        self.base_url = URL(base_url)
        self.trust_env = trust_env
        self.default_encoding = default_encoding

    def build(self) -> httpx.Client:
        return httpx.Client(
            auth=self.auth,
            params=self.params,
            headers=self.headers,
            cookies=self.cookies,
            timeout=self.timeout,
            follow_redirects=self.follow_redirects,
            max_redirects=self.max_redirects,
            event_hooks=self.event_hooks,
            base_url=self.base_url,
            trust_env=self.trust_env,
            default_encoding=self.default_encoding,
        )

    def is_default(self) -> bool:
        return all(
            (
                self.auth == None,
                self.params == QueryParams(),
                self.headers == Headers(),
                self.cookies == Cookies(),
                self.timeout == DEFAULT_TIMEOUT_CONFIG,
                self.follow_redirects == False,
                self.max_redirects == DEFAULT_MAX_REDIRECTS,
                self.event_hooks == {"request": [], "response": []},
                self.base_url == "",
                self.trust_env == True,
                self.default_encoding == "utf-8",
            )
        )

    @classmethod
    def from_client(cls, client: httpx.Client, /) -> "ClientOptions":
        return cls(
            auth=client.auth,
            params=client.params,
            headers=client.headers,
            cookies=client.cookies,
            timeout=client.timeout,
            follow_redirects=client.follow_redirects,
            max_redirects=client.max_redirects,
            event_hooks=client.event_hooks,
            base_url=client.base_url,
            trust_env=client.trust_env,
            default_encoding=client._default_encoding,
        )


@dataclass(init=False)
class RequestOptions:
    method: str
    url: URL
    params: QueryParams
    headers: Headers
    cookies: Cookies
    content: Optional[RequestContent]
    data: Optional[RequestData]
    files: Optional[RequestFiles]
    json: Optional[JsonTypes]
    timeout: Optional[Timeout]

    def __init__(
        self,
        method: MethodTypes,
        url: URLTypes,
        *,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        content: Optional[RequestContent] = None,
        data: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        json: Optional[JsonTypes] = None,
        timeout: Optional[TimeoutTypes] = None,
    ) -> None:
        ...
        self.method = method if isinstance(method, str) else method.decode()
        self.url = URL(url)
        self.params = QueryParams(params)
        self.headers = Headers(headers)
        self.cookies = Cookies(cookies)
        self.content = content
        self.data = data
        self.files = files
        self.json = json
        self.timeout = Timeout(timeout) if timeout is not None else None

    def build_request(self, client: Optional[httpx.Client]) -> httpx.Request:
        if client is None:
            return httpx.Request(
                self.method,
                self.url,
                params=self.params,
                headers=self.headers,
                cookies=self.cookies,
                content=self.content,
                data=self.data,
                files=self.files,
                json=self.json,
                extensions=dict(timeout=self.timeout),
            )
        else:
            return client.build_request(
                self.method,
                self.url,
                params=self.params,
                headers=self.headers,
                cookies=self.cookies,
                content=self.content,
                data=self.data,
                files=self.files,
                json=self.json,
                timeout=self.timeout,
            )


@dataclass
class Specification:
    request: RequestOptions
    response: Optional[Callable[..., Any]] = None
    params: Dict[str, Param] = field(default_factory=dict)
