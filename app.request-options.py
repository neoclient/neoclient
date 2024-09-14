from dataclasses import dataclass
from typing import Any, Optional, Union

import httpx
from httpx import Cookies, Headers, QueryParams, Timeout
from httpx._config import DEFAULT_TIMEOUT_CONFIG
from httpx._types import (
    AuthTypes,
    CookieTypes,
    HeaderTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestExtensions,
    RequestFiles,
    TimeoutTypes,
    URLTypes,
)
from httpx._urls import URL

# TEMP
httpx.Request
httpx.request
httpx.Client.request

MethodTypes = Union[str, bytes]


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
    auth: Optional[AuthTypes]
    follow_redirects: bool
    timeout: Timeout
    extensions: RequestExtensions

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
        auth: Optional[AuthTypes] = None,
        follow_redirects: bool = False,
        timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
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
        self.auth = auth
        self.follow_redirects = follow_redirects
        self.timeout = Timeout(timeout)
        self.extensions = extensions if extensions is not None else {}

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        url = str(self.url)
        return f"<{class_name}({self.method!r}, {url!r})>"


r: RequestOpts = RequestOpts("GET", "/")
