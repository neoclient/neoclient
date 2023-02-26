import urllib.parse
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Dict,
    List,
    MutableMapping,
    Optional,
    Sequence,
    Set,
    Union,
)

import httpx
from httpx import URL, Cookies, Headers, QueryParams, Timeout

from . import converters, utils
from .errors import IncompatiblePathParameters, MissingStateError
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
    RequestExtensions,
    RequestFiles,
    ResponseContent,
    ResponseExtensions,
    SyncByteStream,
    TimeoutTypes,
    URLTypes,
)

__all__: Sequence[str] = (
    "Client",
    "Request",
    "Response",
    "PreRequest",
    "OperationSpecification",
)


class State:
    _state: MutableMapping[str, Any]

    def __init__(self, state: Optional[MutableMapping[str, Any]] = None):
        if state is None:
            state = {}

        super().__setattr__("_state", state)

    def __repr__(self) -> str:
        context: str = ", ".join(
            f"{key}={value!r}"
            for key, value in self._state.items()
        )
        return f"{type(self).__name__}({context})"

    def _set(self, key: str, value: Any) -> None:
        self._state[key] = value

    def _get(self, key: str) -> Any:
        if key in self._state:
            return self._state[key]
        else:
            raise MissingStateError(key=key)

    def _del(self, key: str) -> None:
        del self._state[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._set(key, value)

    def __setattr__(self, key: str, value: Any) -> None:
        self._set(key, value)

    def __getitem__(self, key: str) -> Any:
        return self._get(key)

    def __getattr__(self, key: str) -> Any:
        return self._get(key)

    def __delitem__(self, key: str) -> None:
        self._del(key)

    def __delattr__(self, key: str) -> None:
        self._del(key)


class Request(httpx.Request):
    state: State

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
        extensions: Optional[RequestExtensions] = None,
        state: Optional[State] = None,
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
            self.state = State()

    @classmethod
    def from_httpx_request(cls, request: httpx.Request, /) -> "Request":
        if hasattr(request, "_content"):
            return cls(
                method=request.method,
                url=request.url,
                headers=request.headers,
                extensions=request.extensions,
                content=request.content,
            )
        else:
            return cls(
                method=request.method,
                url=request.url,
                headers=request.headers,
                extensions=request.extensions,
                stream=request.stream,
            )


class Response(httpx.Response):
    state: State

    def __init__(
        self,
        status_code: int,
        *,
        headers: Optional[HeaderTypes] = None,
        content: Optional[ResponseContent] = None,
        text: Optional[str] = None,
        html: Optional[str] = None,
        json: Any = None,
        stream: Union[SyncByteStream, AsyncByteStream, None] = None,
        request: Optional[httpx.Request] = None,
        extensions: Optional[ResponseExtensions] = None,
        history: Optional[List[httpx.Response]] = None,
        default_encoding: Union[str, Callable[[bytes], str]] = "utf-8",
        state: Optional[State] = None,
    ):
        super().__init__(
            status_code=status_code,
            headers=headers,
            content=content,
            text=text,
            html=html,
            json=json,
            stream=stream,
            request=request,
            extensions=extensions,
            history=history,
            default_encoding=default_encoding,
        )

        if state is not None:
            self.state = state
        else:
            self.state = State()

    @classmethod
    def from_httpx_response(cls, response: httpx.Response, /) -> "Response":
        if hasattr(response, "_content"):
            return cls(
                status_code=response.status_code,
                headers=response.headers,
                request=response.request,
                content=response.content,
            )
        else:
            return cls(
                status_code=response.status_code,
                headers=response.headers,
                request=response.request,
                stream=response.stream,
            )


@dataclass(init=False)
class PreRequest:
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
    state: State

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
        state: Optional[State] = None,
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
        self.state = state if state is not None else State()

    def build_request(self, client: Optional[httpx.Client]) -> Request:
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
            httpx_request: httpx.Request = client.build_request(
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

            request: Request = Request.from_httpx_request(httpx_request)

            request.state = self.state

            return request

    def merge(self, pre_request: "PreRequest", /) -> "PreRequest":
        return self.__class__(
            method=pre_request.method,
            url=pre_request.url,
            params=self.params.merge(pre_request.params),
            headers=httpx.Headers({**self.headers, **pre_request.headers}),
            cookies=httpx.Cookies({**self.cookies, **pre_request.cookies}),
            content=(
                pre_request.content
                if pre_request.content is not None
                else self.content
            ),
            data=(
                pre_request.data if pre_request.data is not None else self.data
            ),
            files=(
                pre_request.files
                if pre_request.files is not None
                else self.files
            ),
            json=(
                pre_request.json if pre_request.json is not None else self.json
            ),
            timeout=(
                pre_request.timeout
                if pre_request.timeout is not None
                else self.timeout
            ),
            path_params={
                **self.path_params,
                **pre_request.path_params,
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
