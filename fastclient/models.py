import urllib.parse
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, MutableMapping, Optional, Set

import httpx
from httpx import URL, Cookies, Headers, QueryParams, Timeout
from httpx._auth import Auth
from httpx._config import DEFAULT_MAX_REDIRECTS, DEFAULT_TIMEOUT_CONFIG

from . import converters, utils
from .errors import IncompatiblePathParameters
from .types import (
    AuthTypes,
    CookieTypes,
    DefaultEncodingTypes,
    EventHooks,
    HeaderTypes,
    JsonTypes,
    MethodTypes,
    PathParamTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestFiles,
    TimeoutTypes,
    URLTypes,
)


@dataclass(init=False)
class Client(httpx.Client):
    auth: Optional[Auth]
    params: QueryParams
    headers: Headers
    cookies: Cookies
    timeout: Timeout
    follow_redirects: bool
    max_redirects: int
    event_hooks: Dict[str, List[Callable]]
    base_url: URL
    trust_env: bool


DEFAULT_TRUST_ENV: bool = True
DEFAULT_ENCODING: str = "utf-8"
DEFAULT_FOLLOW_REDIRECTS: bool = False
DEFAULT_BASE_URL: URLTypes = ""
DEFAULT_EVENT_HOOKS: EventHooks = {"request": [], "response": []}


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
        follow_redirects: bool = DEFAULT_FOLLOW_REDIRECTS,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        event_hooks: Optional[EventHooks] = None,
        base_url: URLTypes = DEFAULT_BASE_URL,
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
        self.timeout = (
            converters.convert_timeout(timeout) if timeout is not None else Timeout()
        )
        self.follow_redirects = follow_redirects
        self.max_redirects = max_redirects
        self.event_hooks = (
            event_hooks if event_hooks is not None else DEFAULT_EVENT_HOOKS
        )
        self.base_url = URL(base_url)
        self.trust_env = trust_env
        self.default_encoding = default_encoding

    def build(self) -> httpx.Client:
        return Client(
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
                self.follow_redirects == DEFAULT_FOLLOW_REDIRECTS,
                self.max_redirects == DEFAULT_MAX_REDIRECTS,
                self.event_hooks == DEFAULT_EVENT_HOOKS,
                self.base_url == DEFAULT_BASE_URL,
                self.trust_env == DEFAULT_TRUST_ENV,
                self.default_encoding == DEFAULT_ENCODING,
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
    path_params: MutableMapping[str, str]

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
        path_params: Optional[PathParamTypes] = None,
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

    def build_request(self, client: Optional[httpx.Client]) -> httpx.Request:
        url: str = self._get_formatted_url()

        if client is None:
            return httpx.Request(
                self.method,
                url,
                params=self.params,
                headers=self.headers,
                cookies=self.cookies,
                content=self.content,
                data=self.data,
                files=self.files,
                json=self.json,
                extensions=(
                    dict(timeout=self.timeout.as_dict())
                    if self.timeout is not None
                    else {}
                ),
            )
        else:
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
        raw_url: str = urllib.parse.unquote(str(self.url))

        return utils.partially_format(raw_url, **self.path_params)

    def validate(self):
        url: str = urllib.parse.unquote(str(self.url))

        expected_path_params: Set[str] = utils.get_path_params(url)
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


@dataclass(frozen=True)
class ResolverContext:
    request: RequestOptions
    cached_dependencies: Dict[Callable[..., Any], Any] = field(default_factory=dict)


@dataclass
class ResolutionCache:
    dependencies: MutableMapping[Callable, Any]
