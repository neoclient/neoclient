import urllib.parse
from dataclasses import dataclass
from types import SimpleNamespace
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Set,
    Union,
)

import httpx
from httpx import URL, BaseTransport, Cookies, Headers, Limits, QueryParams, Timeout

from . import converters, utils
from .constants import USER_AGENT
from .defaults import (
    DEFAULT_BASE_URL,
    DEFAULT_ENCODING,
    DEFAULT_FOLLOW_REDIRECTS,
    DEFAULT_LIMITS,
    DEFAULT_MAX_REDIRECTS,
    DEFAULT_TIMEOUT,
    DEFAULT_TRUST_ENV,
)
from .enums import HTTPHeader
from .errors import IncompatiblePathParameters
from .types import (
    AsyncByteStream,
    AuthTypes,
    CertTypes,
    CookiesTypes,
    DefaultEncodingTypes,
    EventHooks,
    HeadersTypes,
    JsonTypes,
    MethodTypes,
    PathParamsTypes,
    ProxiesTypes,
    QueryParamsTypes,
    RequestContent,
    RequestData,
    RequestExtensions,
    RequestFiles,
    ResponseContent,
    ResponseExtensions,
    SyncByteStream,
    TimeoutTypes,
    URLTypes,
    VerifyTypes,
)

__all__: Sequence[str] = (
    # httpx models
    "Cookies",
    "Headers",
    "QueryParams",
    "URL",
    # neoclient models
    "State",
    "ClientOptions",
    "Request",
    "Response",
    "PreRequest",
)


class State(SimpleNamespace, MutableMapping):
    def __init__(
        self, mapping: Optional[Mapping[str, Any]] = None, /, **kwargs: Any
    ) -> None:
        arguments: MutableMapping[str, Any] = {}

        if mapping is not None:
            arguments.update(mapping)

        arguments.update(kwargs)

        super().__init__(**arguments)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    def __getitem__(self, key: str) -> Any:
        if not hasattr(self, key):
            raise KeyError(key)

        return getattr(self, key)

    def __delitem__(self, key: str) -> None:
        if not hasattr(self, key):
            raise KeyError(key)

        delattr(self, key)

    def __len__(self) -> int:
        return len(self.__dict__)

    def __iter__(self) -> Iterator[str]:
        return iter(self.__dict__)


class Request(httpx.Request):
    state: State

    def __init__(
        self,
        method: MethodTypes,
        url: URLTypes,
        *,
        params: Optional[QueryParamsTypes] = None,
        headers: Optional[HeadersTypes] = None,
        cookies: Optional[CookiesTypes] = None,
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
            params=(
                converters.convert_query_params(params) if params is not None else None
            ),
            headers=headers,
            cookies=(
                converters.convert_cookies(cookies) if cookies is not None else None
            ),
            content=content,
            data=data,
            files=files,
            json=json,
            stream=stream,
            extensions=extensions,
        )

        self.state = state if state is not None else State()

    @classmethod
    def from_httpx_request(
        cls, httpx_request: httpx.Request, /, *, state: Optional[State] = None
    ) -> "Request":
        if isinstance(httpx_request, Request):
            return httpx_request

        if hasattr(httpx_request, "_content"):
            request: Request = cls(
                method=httpx_request.method,
                url=httpx_request.url,
                headers=httpx_request.headers,
                extensions=httpx_request.extensions,
                stream=httpx_request.stream,
                state=state,
            )

            request._content = httpx_request.content

            return request

        return cls(
            method=httpx_request.method,
            url=httpx_request.url,
            headers=httpx_request.headers,
            extensions=httpx_request.extensions,
            stream=httpx_request.stream,
            state=state,
        )


class Response(httpx.Response):
    request: Request
    state: State

    def __init__(
        self,
        status_code: int,
        *,
        headers: Optional[HeadersTypes] = None,
        content: Optional[ResponseContent] = None,
        text: Optional[str] = None,
        html: Optional[str] = None,
        json: Any = None,
        stream: Union[SyncByteStream, AsyncByteStream, None] = None,
        request: Optional[Request] = None,
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

        self.state = state if state is not None else State()

    @classmethod
    def from_httpx_response(
        cls, httpx_response: httpx.Response, /, *, state: Optional[State] = None
    ) -> "Response":
        response: Response

        if hasattr(httpx_response, "_content"):
            response = cls(
                status_code=httpx_response.status_code,
                headers=httpx_response.headers,
                # NOTE: Type below temporarily ignored due to #168
                request=httpx_response.request,  # type: ignore
                stream=httpx_response.stream,
                state=state,
            )

            response._content = httpx_response.content
        else:
            response = cls(
                status_code=httpx_response.status_code,
                headers=httpx_response.headers,
                # NOTE: Type below temporarily ignored due to #168
                request=httpx_response.request,  # type: ignore
                stream=httpx_response.stream,
                state=state,
            )

        response.history = httpx_response.history

        return response


@dataclass(init=False)
class ClientOptions:
    auth: Optional[AuthTypes]
    params: QueryParams
    headers: Headers
    cookies: Cookies
    verify: VerifyTypes
    cert: Optional[CertTypes]
    http1: bool
    http2: bool
    proxies: Optional[ProxiesTypes]
    mounts: Mapping[str, BaseTransport]
    timeout: Timeout
    follow_redirects: bool
    limits: Limits
    max_redirects: int
    event_hooks: EventHooks
    base_url: URL
    transport: Optional[BaseTransport]
    app: Optional[Callable[..., Any]]
    trust_env: bool
    default_encoding: DefaultEncodingTypes

    def __init__(
        self,
        auth: Optional[AuthTypes] = None,
        params: Optional[QueryParamsTypes] = None,
        headers: Optional[HeadersTypes] = None,
        cookies: Optional[CookiesTypes] = None,
        verify: VerifyTypes = True,
        cert: Optional[CertTypes] = None,
        http1: bool = True,
        http2: bool = False,
        proxies: Optional[ProxiesTypes] = None,
        mounts: Optional[Mapping[str, BaseTransport]] = None,
        timeout: TimeoutTypes = DEFAULT_TIMEOUT,
        follow_redirects: bool = DEFAULT_FOLLOW_REDIRECTS,
        limits: Limits = DEFAULT_LIMITS,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        event_hooks: Optional[EventHooks] = None,
        base_url: URLTypes = DEFAULT_BASE_URL,
        transport: Optional[BaseTransport] = None,
        app: Optional[Callable[..., Any]] = None,
        trust_env: bool = DEFAULT_TRUST_ENV,
        default_encoding: DefaultEncodingTypes = DEFAULT_ENCODING,
    ) -> None:
        self.auth = auth
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
        self.verify = verify
        self.cert = cert
        self.http1 = http1
        self.http2 = http2
        self.proxies = proxies
        self.mounts = mounts if mounts is not None else {}
        self.timeout = (
            converters.convert_timeout(timeout) if timeout is not None else Timeout()
        )
        self.follow_redirects = follow_redirects
        self.limits = limits
        self.max_redirects = max_redirects
        self.event_hooks = (
            event_hooks if event_hooks is not None else {"request": [], "response": []}
        )
        self.base_url = URL(base_url)
        self.transport = transport
        self.app = app
        self.trust_env = trust_env
        self.default_encoding = default_encoding

    def build(self) -> httpx.Client:
        headers: Headers = Headers(self.headers)

        # Set a default User-Agent header
        headers.setdefault(HTTPHeader.USER_AGENT, USER_AGENT)

        return httpx.Client(
            auth=self.auth,
            params=self.params,
            headers=headers,
            cookies=self.cookies,
            verify=self.verify,
            cert=self.cert,
            http1=self.http1,
            http2=self.http2,
            proxies=self.proxies,
            mounts=self.mounts,
            timeout=self.timeout,
            follow_redirects=self.follow_redirects,
            limits=self.limits,
            max_redirects=self.max_redirects,
            event_hooks=self.event_hooks,
            base_url=self.base_url,
            transport=self.transport,
            app=self.app,
            trust_env=self.trust_env,
            default_encoding=self.default_encoding,
        )


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
    follow_redirects: bool

    def __init__(
        self,
        method: MethodTypes,
        url: URLTypes,
        *,
        params: Optional[QueryParamsTypes] = None,
        headers: Optional[HeadersTypes] = None,
        cookies: Optional[CookiesTypes] = None,
        content: Optional[RequestContent] = None,
        data: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        json: Optional[JsonTypes] = None,
        timeout: Optional[TimeoutTypes] = None,
        path_params: Optional[PathParamsTypes] = None,
        state: Optional[State] = None,
        follow_redirects: bool = DEFAULT_FOLLOW_REDIRECTS,
    ) -> None:
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
        self.follow_redirects = follow_redirects

    def __repr__(self) -> str:
        return f"<{type(self).__name__}({str(self.method)!r}, {str(self.url)!r})>"

    def __eq__(self, rhs: Any, /) -> bool:
        if not isinstance(rhs, PreRequest):
            return False

        pre_request: PreRequest = rhs

        return all(
            (
                self.method == pre_request.method,
                self.url == pre_request.url,
                self.params == pre_request.params,
                self.headers == pre_request.headers,
                self.cookies == pre_request.cookies,
                self.content == pre_request.content,
                self.data == pre_request.data,
                self.files == pre_request.files,
                self.json == pre_request.json,
                self.timeout == pre_request.timeout,
                self.path_params == pre_request.path_params,
                self.state == pre_request.state,
                self.follow_redirects == pre_request.follow_redirects,
            )
        )

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

        request: Request = Request.from_httpx_request(httpx_request, state=self.state)

        return request

    def merge(self, pre_request: "PreRequest", /) -> "PreRequest":
        return self.__class__(
            method=pre_request.method,
            url=pre_request.url,
            params=self.params.merge(pre_request.params),
            headers=httpx.Headers({**self.headers, **pre_request.headers}),
            cookies=httpx.Cookies({**self.cookies, **pre_request.cookies}),
            content=(
                pre_request.content if pre_request.content is not None else self.content
            ),
            data=(pre_request.data if pre_request.data is not None else self.data),
            files=(pre_request.files if pre_request.files is not None else self.files),
            json=(pre_request.json if pre_request.json is not None else self.json),
            timeout=(
                pre_request.timeout if pre_request.timeout is not None else self.timeout
            ),
            path_params={
                **self.path_params,
                **pre_request.path_params,
            },
            state=State({**self.state, **pre_request.state}),
            follow_redirects=self.follow_redirects and pre_request.follow_redirects,
        )

    def clone(self) -> "PreRequest":
        return self.merge(
            PreRequest(
                method=self.method,
                url=self.url,
                follow_redirects=self.follow_redirects,
            )
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
