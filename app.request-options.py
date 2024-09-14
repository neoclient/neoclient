from dataclasses import dataclass
from typing import Any, Optional, Union

import httpx
from httpx import Client, Cookies, Headers, QueryParams, Timeout
from httpx._config import DEFAULT_TIMEOUT_CONFIG
from httpx._types import (
    AsyncByteStream,
    AuthTypes,
    CertTypes,
    CookieTypes,
    HeaderTypes,
    ProxiesTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestExtensions,
    RequestFiles,
    SyncByteStream,
    TimeoutTypes,
    URLTypes,
    VerifyTypes,
)
from httpx._client import UseClientDefault, USE_CLIENT_DEFAULT
from httpx._urls import URL

# TEMP
httpx.Request
httpx.request
httpx.Client.request

MethodTypes = Union[str, bytes]

# Request, RequestMeta, RequestOpts, RequestOptions
# PreRequest, ...
@dataclass
class RequestOpts:
    method: str
    url: URL
    params: QueryParams
    headers: Headers
    cookies: Cookies
    content: Optional[RequestContent]
    data: Optional[RequestData]
    files: Optional[RequestFiles]
    json: Optional[Any]
    # auth: Optional[AuthTypes]
    timeout: Optional[Timeout]
    extensions: RequestExtensions
    # Sending: <-- include
    #   auth
    #   follow_redirects
    # Client:
    #   verify
    #   cert
    #   trust_env
    #   proxies

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
        json: Optional[Any] = None,
        # auth: Optional[AuthTypes] = None,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: Optional[RequestExtensions] = None,
    ) -> None:
        self.method = (
            method.decode("ascii").upper()
            if isinstance(method, bytes)
            else method.upper()
        )
        self.url = URL(url)
        self.params = QueryParams(params)
        self.headers = Headers(headers)
        self.cookies = Cookies(cookies)
        self.content = content
        self.data = data
        self.files = files
        self.json = json
        # self.auth = auth
        self.timeout = None if timeout is isinstance(timeout, UseClientDefault) else Timeout(timeout)
        self.extensions = extensions if extensions is not None else {}

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        url = str(self.url)
        return f"<{class_name}({self.method!r}, {url!r})>"

    # def build(self) -> httpx.Request:
    #     raise NotImplementedError
    
    # def send(self, client: Optional[Client] = None) -> httpx.Request:
    #     raise NotImplementedError


r: RequestOpts = RequestOpts("GET", "/")


# httpx.request(...)
# @dataclass
# class Request1:
    # method: str
    # url: URLTypes
    # params: Optional[QueryParamTypes] = None
    # content: Optional[RequestContent] = None
    # data: Optional[RequestData] = None
    # files: Optional[RequestFiles] = None
    # json: Optional[Any] = None
    # headers: Optional[HeaderTypes] = None
    # cookies: Optional[CookieTypes] = None
    # auth: Optional[AuthTypes] = None
    # proxies: Optional[ProxiesTypes] = None
    # timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG
    # Sending:
    # follow_redirects: bool = False
    # Client:
    # verify: VerifyTypes = True
    # cert: Optional[CertTypes] = None
    # trust_env: bool = True


# httpx.Request
# @dataclass
# class Request2:
    # method: Union[str, bytes]
    # url: Union["URL", str]
    # params: Optional[QueryParamTypes] = None
    # headers: Optional[HeaderTypes] = None
    # cookies: Optional[CookieTypes] = None
    # content: Optional[RequestContent] = None
    # data: Optional[RequestData] = None
    # files: Optional[RequestFiles] = None
    # json: Optional[Any] = None
    # stream: Union[SyncByteStream, AsyncByteStream, None] = None
    # extensions: Optional[RequestExtensions] = None


# httpx.Client.request(...)
# class Request3:
    # method: str
    # url: URLTypes
    # content: Optional[RequestContent] = None
    # data: Optional[RequestData] = None
    # files: Optional[RequestFiles] = None
    # json: Optional[Any] = None
    # params: Optional[QueryParamTypes] = None
    # headers: Optional[HeaderTypes] = None
    # cookies: Optional[CookieTypes] = None
    # auth: Union[AuthTypes, UseClientDefault, None] = USE_CLIENT_DEFAULT
    # follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT
    # timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT
    # extensions: Optional[RequestExtensions] = None
