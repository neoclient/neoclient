import urllib.parse
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Dict,
    MutableMapping,
    Optional,
    Sequence,
    Set,
    Union,
)

import httpx
from httpx import URL, Cookies, Headers, QueryParams, Timeout

from . import converters, utils
from .errors import IncompatiblePathParameters
from .middleware import Middleware
from .types import (
    AsyncByteStream,
    CookiesTypes,
    CookieTypes,
    HeadersTypes,
    HeaderTypes,
    JsonTypes,
    MethodTypes,
    PathsTypes,
    QueriesTypes,
    RequestContent,
    RequestData,
    RequestFiles,
    SyncByteStream,
    TimeoutTypes,
    URLTypes,
)

__all__: Sequence[str] = (
    "Client",
    "Request",
    "RequestOptions",
    "OperationSpecification",
)


class Request(httpx.Request):
    state: MutableMapping[str, Any]

    def __init__(
        self,
        method: MethodTypes,
        url: URLTypes,
        *,
        params: Optional[QueriesTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        content: Optional[RequestContent] = None,
        data: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        json: Optional[Any] = None,
        stream: Union[SyncByteStream, AsyncByteStream, None] = None,
        extensions: Optional[dict] = None,
        state: Optional[MutableMapping[str, Any]] = None,
    ):
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
            stream=stream,
            extensions=extensions,
        )

        if state is not None:
            self.state = state
        else:
            self.state = {}


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
    path_params: MutableMapping[str, str]
    state: MutableMapping[str, Any]

    def __init__(
        self,
        method: MethodTypes,
        url: URLTypes,
        *,
        params: Optional[QueriesTypes] = None,
        headers: Optional[HeadersTypes] = None,
        cookies: Optional[CookiesTypes] = None,
        content: Optional[RequestContent] = None,
        data: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        json: Optional[JsonTypes] = None,
        timeout: Optional[TimeoutTypes] = None,
        path_params: Optional[PathsTypes] = None,
    ) -> None:
        ...
        self.method = method if isinstance(method, str) else method.decode()
        self.url = URL(url)
        self.params = (
            converters.convert_query_params(params)
            if params is not None
            else QueryParams()
        )
        self.headers = (
            converters.convert_headers(headers) if headers is not None else Headers()
        )
        self.cookies = (
            converters.convert_cookies(cookies) if cookies is not None else Cookies()
        )
        self.content = content
        self.data = data
        self.files = files
        self.json = json
        self.timeout = (
            converters.convert_timeout(timeout) if timeout is not None else None
        )
        self.path_params = (
            converters.convert_path_params(path_params)
            if path_params is not None
            else {}
        )
        self.state = {}

    def build_request(self, client: Optional[httpx.Client]) -> httpx.Request:
        url: str = self._get_formatted_url()

        extensions: Dict[str, Any] = {}

        if client is None:
            if self.timeout is not None:
                extensions["timeout"] = self.timeout.as_dict()

            return Request(
                self.method,
                url,
                params=self.params,
                headers=self.headers,
                cookies=self.cookies,
                content=self.content,
                data=self.data,
                files=self.files,
                json=self.json,
                extensions=extensions,
                state=self.state,
            )
        else:
            # TODO: Somehow make this return a `Request`, not a `httpx.Request`
            return client.build_request(
                self.method,
                url,
                params=self.params,
                headers=self.headers,
                cookies=self.cookies,
                content=self.content,
                data=self.data,
                files=self.files,
                json=self.json,
                timeout=self.timeout,
                extensions=extensions,
            )

    def merge(self, request_options: "RequestOptions", /) -> "RequestOptions":
        return self.__class__(
            method=request_options.method,
            url=request_options.url,
            params=self.params.merge(request_options.params),
            headers=httpx.Headers({**self.headers, **request_options.headers}),
            cookies=httpx.Cookies({**self.cookies, **request_options.cookies}),
            content=(
                request_options.content
                if request_options.content is not None
                else self.content
            ),
            data=(
                request_options.data if request_options.data is not None else self.data
            ),
            files=(
                request_options.files
                if request_options.files is not None
                else self.files
            ),
            json=(
                request_options.json if request_options.json is not None else self.json
            ),
            timeout=(
                request_options.timeout
                if request_options.timeout is not None
                else self.timeout
            ),
            path_params={
                **self.path_params,
                **request_options.path_params,
            },
        )

    def _get_formatted_url(self) -> str:
        return urllib.parse.unquote(str(self.url)).format(**self.path_params)

    def validate(self):
        url: str = urllib.parse.unquote(str(self.url))

        expected_path_params: Set[str] = utils.parse_format_string(url)
        actual_path_params: Set[str] = set(self.path_params.keys())

        # Validate path params are correct
        if expected_path_params != actual_path_params:
            raise IncompatiblePathParameters(
                f"Expected {tuple(expected_path_params)}, got {tuple(actual_path_params)}"
            )


@dataclass
class OperationSpecification:
    request: RequestOptions
    response: Optional[Callable[..., Any]] = None
    middleware: Middleware = field(default_factory=Middleware)
