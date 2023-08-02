import dataclasses
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    MutableSequence,
    Optional,
    Sequence,
    TypeVar,
)

import httpx
from httpx import URL, BaseTransport, Cookies, Headers, Limits, QueryParams, Timeout
from httpx._auth import Auth
from mediate.protocols import MiddlewareCallable
from roster import Record
from typing_extensions import ParamSpec

from . import converters
from .composition import get_fields, validate_fields
from .constants import USER_AGENT
from .defaults import (
    DEFAULT_AUTH,
    DEFAULT_BASE_URL,
    DEFAULT_COOKIES,
    DEFAULT_ENCODING,
    DEFAULT_EVENT_HOOKS,
    DEFAULT_FOLLOW_REDIRECTS,
    DEFAULT_HEADERS,
    DEFAULT_LIMITS,
    DEFAULT_MAX_REDIRECTS,
    DEFAULT_PARAMS,
    DEFAULT_TIMEOUT,
    DEFAULT_TRUST_ENV,
)
from .enums import HTTPHeader, HTTPMethod
from .middleware import Middleware
from .models import ClientOptions, PreRequest, Request, Response
from .operation import Operation, get_operation
from .types import (
    AuthTypes,
    CertTypes,
    CookiesTypes,
    DefaultEncodingTypes,
    EventHooks,
    HeadersTypes,
    ProxiesTypes,
    QueriesTypes,
    TimeoutTypes,
    URLTypes,
    VerifyTypes,
)

__all__: Sequence[str] = (
    "Session",
    "Client",
    "NeoClient",
)


T = TypeVar("T")

PS = ParamSpec("PS")
RT = TypeVar("RT")

C = TypeVar("C", bound=Callable[..., Any])


class BaseService:
    def __repr__(self) -> str:
        return f"{type(self).__name__}()"


@dataclass(init=False)
class Session(httpx.Client):
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

    def __init__(
        self,
        base_url: URLTypes = DEFAULT_BASE_URL,
        *,
        auth: Optional[AuthTypes] = DEFAULT_AUTH,
        params: Optional[QueriesTypes] = DEFAULT_PARAMS,
        headers: Optional[HeadersTypes] = DEFAULT_HEADERS,
        cookies: Optional[CookiesTypes] = DEFAULT_COOKIES,
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
        event_hooks: Optional[EventHooks] = DEFAULT_EVENT_HOOKS,
        transport: Optional[BaseTransport] = None,
        app: Optional[Callable[..., Any]] = None,
        trust_env: bool = DEFAULT_TRUST_ENV,
        default_encoding: DefaultEncodingTypes = DEFAULT_ENCODING,
    ) -> None:
        params = (
            converters.convert_query_params(params)
            if params is not None
            else QueryParams()
        )
        headers = (
            converters.convert_headers(headers) if headers is not None else Headers()
        )
        cookies = (
            converters.convert_cookies(cookies) if cookies is not None else Cookies()
        )
        timeout = (
            converters.convert_timeout(timeout) if timeout is not None else Timeout()
        )
        base_url = URL(base_url)

        headers.setdefault(HTTPHeader.USER_AGENT, USER_AGENT)

        super().__init__(
            auth=auth,
            params=params,
            headers=headers,
            cookies=cookies,
            verify=verify,
            cert=cert,
            http1=http1,
            http2=http2,
            proxies=proxies,
            mounts=mounts,
            timeout=timeout,
            follow_redirects=follow_redirects,
            limits=limits,
            max_redirects=max_redirects,
            event_hooks=event_hooks,
            transport=transport,
            app=app,
            base_url=base_url,
            trust_env=trust_env,
            default_encoding=default_encoding,
        )


@dataclass(init=False)
class Client:
    client: Optional[httpx.Client]
    middleware: Middleware
    default_response: Optional[Callable[..., Any]] = None
    dependencies: MutableSequence[Callable[..., Any]] = field(default_factory=list)

    def __init__(
        self,
        client: Optional[httpx.Client] = None,
        middleware: Optional[Middleware] = None,
        default_response: Optional[Callable[..., Any]] = None,
        dependencies: Optional[Sequence[Callable[..., Any]]] = None,
    ) -> None:
        self.client = client
        self.middleware = middleware if middleware is not None else Middleware()
        self.default_response = default_response
        self.dependencies = [*dependencies] if dependencies is not None else []

    def bind(self, func: Callable[PS, RT], /) -> Callable[PS, RT]:
        operation: Operation = get_operation(func)

        # Create a clone of the operation's middleware, so that when the client's
        # middleware gets added, it doesn't mutate the original
        middleware: Middleware = Middleware()

        middleware.add_all(operation.middleware.record)

        # Create a clone of the operation's dependencies, so that when the client's
        # dependencies get added, it doesn't mutate the original
        dependencies: MutableSequence[Callable[..., Any]] = []

        dependencies.extend(operation.dependencies)

        bound_operation: Operation[PS, RT] = dataclasses.replace(
            operation,
            client=self.client,
            middleware=middleware,
            dependencies=dependencies,
        )

        # If the operation doesn't have a response, use the client's default response
        # if one is available
        if bound_operation.response is None and self.default_response is not None:
            bound_operation.response = self.default_response

        # Add the client's middleware
        bound_operation.middleware.add_all(self.middleware.record)

        # Add the client's dependencies
        dependencies.extend(self.dependencies)

        return bound_operation.wrapper

    def request(
        self,
        method: str,
        endpoint: str,
        /,
        *,
        response: Optional[Callable] = None,
    ) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
        client_options: ClientOptions = ClientOptions()
        request_options: PreRequest = PreRequest(
            method=method,
            url=endpoint,
        )

        operation_response: Optional[Callable] = None

        if response is not None:
            operation_response = response
        elif self.default_response is not None:
            operation_response = self.default_response

        def decorator(func: Callable[PS, RT], /) -> Callable[PS, RT]:
            middleware: Middleware = Middleware()

            # Add the client's middleware
            middleware.add_all(self.middleware.record)

            dependencies: MutableSequence[Callable[..., Any]] = []

            # Add the client's dependencies
            dependencies.extend(self.dependencies)

            operation: Operation[PS, RT] = Operation(
                func=func,
                client_options=client_options,
                request_options=request_options,
                client=self.client,
                middleware=middleware,
                response=operation_response,
                dependencies=dependencies,
            )

            # Validate operation function parameters are acceptable
            validate_fields(get_fields(operation.request_options, func))

            return operation.wrapper

        return decorator

    def put(
        self, endpoint: str, /, *, response: Optional[Callable] = None
    ) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
        return self.request(HTTPMethod.PUT.name, endpoint, response=response)

    def get(
        self, endpoint: str, /, *, response: Optional[Callable] = None
    ) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
        return self.request(HTTPMethod.GET.name, endpoint, response=response)

    def post(
        self, endpoint: str, /, *, response: Optional[Callable] = None
    ) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
        return self.request(HTTPMethod.POST.name, endpoint, response=response)

    def head(
        self, endpoint: str, /, *, response: Optional[Callable] = None
    ) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
        return self.request(HTTPMethod.HEAD.name, endpoint, response=response)

    def patch(
        self, endpoint: str, /, *, response: Optional[Callable] = None
    ) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
        return self.request(HTTPMethod.PATCH.name, endpoint, response=response)

    def delete(
        self, endpoint: str, /, *, response: Optional[Callable] = None
    ) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
        return self.request(HTTPMethod.DELETE.name, endpoint, response=response)

    def options(
        self, endpoint: str, /, *, response: Optional[Callable] = None
    ) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
        return self.request(HTTPMethod.OPTIONS.name, endpoint, response=response)

    def depends(self, target: C, /) -> C:
        self.dependencies.append(target)

        return target


class NeoClient(Client):
    def __init__(
        self,
        base_url: URLTypes = DEFAULT_BASE_URL,
        *,
        auth: Optional[AuthTypes] = DEFAULT_AUTH,
        params: Optional[QueriesTypes] = DEFAULT_PARAMS,
        headers: Optional[HeadersTypes] = DEFAULT_HEADERS,
        cookies: Optional[CookiesTypes] = DEFAULT_COOKIES,
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
        event_hooks: Optional[EventHooks] = DEFAULT_EVENT_HOOKS,
        transport: Optional[BaseTransport] = None,
        app: Optional[Callable[..., Any]] = None,
        trust_env: bool = DEFAULT_TRUST_ENV,
        default_encoding: DefaultEncodingTypes = DEFAULT_ENCODING,
        middleware: Optional[Sequence[MiddlewareCallable[Request, Response]]] = None,
        default_response: Optional[Callable[..., Any]] = None,
        dependencies: Optional[Sequence[Callable[..., Any]]] = None,
    ) -> None:
        super().__init__(
            client=Session(
                auth=auth,
                params=params,
                headers=headers,
                cookies=cookies,
                verify=verify,
                cert=cert,
                http1=http1,
                http2=http2,
                proxies=proxies,
                mounts=mounts,
                timeout=timeout,
                follow_redirects=follow_redirects,
                limits=limits,
                max_redirects=max_redirects,
                event_hooks=event_hooks,
                transport=transport,
                app=app,
                base_url=base_url,
                trust_env=trust_env,
                default_encoding=default_encoding,
            ),
            middleware=(
                Middleware(record=Record(middleware))
                if middleware is not None
                else Middleware()
            ),
            default_response=default_response,
            dependencies=(dependencies if dependencies is not None else []),
        )
