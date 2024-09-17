import dataclasses
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
from typing_extensions import Self

import httpx
from httpx import (
    URL,
    BaseTransport,
    Client,
    Cookies,
    Headers,
    Limits,
    QueryParams,
    Timeout,
)
from httpx._client import UseClientDefault, USE_CLIENT_DEFAULT

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
    "RequestOpts",
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
    extensions: RequestExtensions

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
        self.auth = auth
        self.follow_redirects = follow_redirects
        # NOTE: Should `converters.convert_timeout` be used here?
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

    def send(self, client: Optional[Client] = None) -> httpx.Response:
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
            timeout=self.timeout
            if self.timeout is not None
            else USE_CLIENT_DEFAULT,  #  type: ignore
        )

    def validate(self) -> None:
        return


@dataclass(repr=False)
class RequestOpts(BaseRequestOpts):
    path_params: MutableMapping[str, str]
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

    def validate(self):
        # NOTE: Does URL encoding affect this?
        url: str = str(self.url)

        expected_path_params: Set[str] = utils.parse_format_string(url)
        actual_path_params: Set[str] = set(self.path_params.keys())

        # Validate path params are correct
        if expected_path_params != actual_path_params:
            raise IncompatiblePathParameters(
                f"Expected {tuple(expected_path_params)}, got {tuple(actual_path_params)}"
            )
