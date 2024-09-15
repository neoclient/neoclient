from dataclasses import dataclass
import dataclasses
from typing import Any, MutableMapping, Optional, Union
from typing_extensions import Self

import httpx
from neoclient import Request
from httpx import Client, Cookies, Headers, QueryParams, Response, Timeout
from httpx._client import UseClientDefault, USE_CLIENT_DEFAULT
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

from neoclient import converters
from neoclient.models import State
from neoclient.types import PathParamsTypes

MethodTypes = Union[str, bytes]


@dataclass
class BaseRequestOpts:
    # Note: These opts match the signature of httpx.Client.request
    method: str
    url: URL
    content: Optional[RequestContent]
    data: Optional[RequestData]
    files: Optional[RequestFiles]
    json: Optional[Any]
    params: QueryParams
    headers: Headers
    cookies: Cookies
    auth: Optional[AuthTypes]
    follow_redirects: bool
    timeout: Optional[Timeout]
    # timeout: Union[Timeout, UseClientDefault]
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
        self.auth = auth
        self.follow_redirects = follow_redirects
        self.timeout = (
            Timeout(timeout) if not isinstance(timeout, UseClientDefault) else None
        )
        self.extensions = extensions if extensions is not None else {}

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        url = str(self.url)
        return f"<{class_name}({self.method!r}, {url!r})>"

    def build(self, client: Optional[Client] = None) -> httpx.Request:
        if client is None:
            client = Client()

        return client.build_request(
            method=self.method,
            url=self.url,
            content=self.content,
            data=self.data,
            files=self.files,
            json=self.json,
            params=self.params,
            headers=self.headers,
            cookies=self.cookies,
            timeout=self.timeout if self.timeout is not None else USE_CLIENT_DEFAULT,
            extensions=self.extensions,
        )

    def send(self, client: Optional[Client] = None) -> Response:
        if client is None:
            client = Client()

        request: httpx.Request = self.build(client)

        return client.send(
            request,
            auth=self.auth,
            follow_redirects=self.follow_redirects,
        )

    def copy(self) -> Self:
        return dataclasses.replace(
            self,
            timeout=self.timeout if self.timeout is not None else USE_CLIENT_DEFAULT, #  type: ignore
        )


@dataclass(repr=False)
class RequestOpts(BaseRequestOpts):
    path_params: MutableMapping[str, str]
    state: State

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
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: Optional[RequestExtensions] = None,
        # Extras
        path_params: Optional[PathParamsTypes] = None,
        state: Optional[State] = None,
    ) -> None:
        super().__init__(
            method=method,
            url=url,
            params=params,
            headers=headers,
            cookies=cookies,
            content=content,
            data=data,
            files=files,
            json=json,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )

        self.path_params = (
            converters.convert_path_params(path_params)
            if path_params is not None
            else {}
        )
        self.state = state if state is not None else State()

    def build(self, client: Optional[Client] = None) -> Request:
        request_opts: RequestOpts = dataclasses.replace(self, url=self.formatted_url)
        request: httpx.Request = BaseRequestOpts.build(request_opts, client)

        return Request.from_httpx_request(request, state=self.state)

    @property
    def formatted_url(self) -> URL:
        # NOTE: Does URL encoding affect this?
        return URL(str(self.url).format(**self.path_params))

    # TODO: merge, validate


r: RequestOpts = RequestOpts(
    "GET",
    "/eat/{food}?desert={desert}&cond_sauces={sauces}",
    path_params={"food": "pizza", "desert": "chocolate", "sauces": "ketchup"},
)
