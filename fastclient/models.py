import urllib.parse
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    MutableMapping,
    MutableSequence,
    Optional,
    Set,
)

import httpx
from httpx import URL, Cookies, Headers, QueryParams, Timeout
from httpx._auth import Auth
from httpx._config import DEFAULT_MAX_REDIRECTS, DEFAULT_TIMEOUT_CONFIG
from param.models import Parameter

from . import utils, converters
from .typs import PathParams
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


# NOTE: This does not belong here
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
    path_params: PathParams

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
        self.params = QueryParams(params)
        self.headers = Headers(headers)
        self.cookies = Cookies(cookies)
        self.content = content
        self.data = data
        self.files = files
        self.json = json
        self.timeout = Timeout(timeout) if timeout is not None else None
        self.path_params = (
            converters.convert_path_params(path_params)
            if path_params is not None
            else PathParams()
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
            path_params=PathParams(
                args=[*self.path_params.args, *request_options.path_params.args],
                kwargs={
                    **self.path_params.kwargs,
                    **request_options.path_params.kwargs,
                },
            ),
        )

    # def add_query_param(self, key: str, value: Any) -> None:
    #     self.params = self.params.set(key, value)

    # def add_header(self, key: str, value: str) -> None:
    #     self.headers[key] = value

    # def add_cookie(self, key: str, value: str) -> None:
    #     self.cookies[key] = value

    # def add_path_param(self, key: str, value: Any) -> None:
    #     self.path_params[key] = value

    # def add_query_params(self, query_params: QueryParamTypes, /) -> None:
    #     self.params = self.params.merge(httpx.QueryParams(query_params))

    # def add_headers(self, headers: HeaderTypes, /) -> None:
    #     self.headers.update(httpx.Headers(headers))

    # def add_cookies(self, cookies: CookieTypes, /) -> None:
    #     self.cookies.update(httpx.Cookies(cookies))

    # def add_path_params(self, path_params: Mapping[str, Any], /) -> None:
    #     self.path_params.update(path_params)

    def _get_formatted_url(self) -> str:
        raw_url: str = urllib.parse.unquote(str(self.url))

        return utils.partially_format(
            raw_url,
            **self.path_params.kwargs,
            # NOTE: As a *temporary* solution, positional path parameters are
            # currently inserted into the key `pp`... this is obviously not the correct
            # way to do this going forward.
            pp="/".join(self.path_params.args),
        )

    def validate(self):
        formatted_url: str = self._get_formatted_url()

        missing_path_params: Set[str] = utils.get_path_params(formatted_url)

        # Validate path params are correct
        if missing_path_params:
            raise IncompatiblePathParameters(
                f"Incompatible path params. Missing: {missing_path_params}"
            )


@dataclass
class OperationSpecification:
    request: RequestOptions
    response: Optional[Callable[..., Any]] = None


@dataclass(frozen=True)
class ComposerContext:
    request: RequestOptions
    parameters: Dict[str, Parameter] = field(default_factory=dict)


@dataclass(frozen=True)
class ResolverContext:
    request: RequestOptions
    cached_dependencies: Dict[Callable[..., Any], Any] = field(default_factory=dict)
