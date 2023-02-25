import dataclasses
import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Type, TypeVar

import httpx
from httpx import URL, Cookies, Headers, QueryParams, Response, Timeout
from httpx._auth import Auth
from mediate.protocols import MiddlewareCallable
from roster import Record
from typing_extensions import ParamSpec

from . import __version__, converters
from .composition import get_fields, validate_fields
from .defaults import (
    DEFAULT_AUTH,
    DEFAULT_BASE_URL,
    DEFAULT_COOKIES,
    DEFAULT_ENCODING,
    DEFAULT_EVENT_HOOKS,
    DEFAULT_FOLLOW_REDIRECTS,
    DEFAULT_HEADERS,
    DEFAULT_MAX_REDIRECTS,
    DEFAULT_PARAMS,
    DEFAULT_TIMEOUT,
    DEFAULT_TRUST_ENV,
)
from .enums import HeaderName, HttpMethod, MethodKind
from .middleware import Middleware
from .models import RequestOptions, Request
from .operation import Operation, OperationSpecification, get_operation, has_operation
from .types import (
    AuthTypes,
    CookiesTypes,
    DefaultEncodingTypes,
    EventHooks,
    HeadersTypes,
    QueriesTypes,
    TimeoutTypes,
    URLTypes,
)
from .utils import get_method_kind

__all__: Sequence[str] = (
    "Session",
    "Client",
    "NeoClient",
)


T = TypeVar("T")

PS = ParamSpec("PS")
RT = TypeVar("RT")

USER_AGENT: str = f"neoclient/{__version__}"


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
        timeout: TimeoutTypes = DEFAULT_TIMEOUT,
        follow_redirects: bool = DEFAULT_FOLLOW_REDIRECTS,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        event_hooks: Optional[EventHooks] = DEFAULT_EVENT_HOOKS,
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

        headers.setdefault(HeaderName.USER_AGENT, USER_AGENT)

        super().__init__(
            auth=auth,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            follow_redirects=follow_redirects,
            max_redirects=max_redirects,
            event_hooks=event_hooks,
            base_url=base_url,
            trust_env=trust_env,
            default_encoding=default_encoding,
        )


@dataclass(init=False)
class Client:
    client: Optional[httpx.Client]
    middleware: Middleware

    def __init__(
        self,
        client: Optional[httpx.Client] = None,
        middleware: Optional[Middleware] = None,
    ) -> None:
        self.client = client
        self.middleware = middleware if middleware is not None else Middleware()

    def create(self, protocol: Type[T], /) -> T:
        operations: Mapping[str, Callable] = {
            member_name: member
            for member_name, member in inspect.getmembers(protocol)
            if has_operation(member)
        }

        attributes: dict = {"__module__": protocol.__module__}

        func: Callable
        for func in operations.values():
            static_attr = inspect.getattr_static(protocol, func.__name__)

            attributes[func.__name__] = static_attr

        typ: Type[BaseService] = type(protocol.__name__, (BaseService,), attributes)

        obj: T = typ()  # type: ignore

        member_name: str
        member: Any
        for member_name, member in inspect.getmembers(obj):
            if not has_operation(member):
                continue

            bound_member: Callable = self.bind(member)

            method_kind: MethodKind = get_method_kind(member)

            if method_kind is MethodKind.METHOD:
                bound_member = bound_member.__get__(obj)
            elif method_kind is MethodKind.CLASS_METHOD:
                bound_member = bound_member.__get__(typ)

            operation: Operation = get_operation(bound_member)

            operation.func = bound_member

            setattr(obj, member_name, bound_member)

        return obj

    def bind(self, func: Callable[PS, RT], /) -> Callable[PS, RT]:
        operation: Operation = get_operation(func)

        bound_operation: Operation[PS, RT] = dataclasses.replace(
            operation, client=self.client
        )

        return bound_operation.wrapper

    def request(
        self,
        method: str,
        endpoint: str,
        /,
        *,
        response: Optional[Callable] = None,
    ) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
        specification: OperationSpecification = OperationSpecification(
            request=RequestOptions(
                method=method,
                url=endpoint,
            ),
            response=response,
        )

        def decorator(func: Callable[PS, RT], /) -> Callable[PS, RT]:
            operation: Operation[PS, RT] = Operation(
                func=func,
                specification=specification,
                client=self.client,
                middleware=self.middleware,
            )

            # Validate operation function parameters are acceptable
            validate_fields(get_fields(specification.request, func))

            return operation.wrapper

        return decorator

    def put(
        self, endpoint: str, /, *, response: Optional[Callable] = None
    ) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
        return self.request(HttpMethod.PUT.name, endpoint, response=response)

    def get(
        self, endpoint: str, /, *, response: Optional[Callable] = None
    ) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
        return self.request(HttpMethod.GET.name, endpoint, response=response)

    def post(
        self, endpoint: str, /, *, response: Optional[Callable] = None
    ) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
        return self.request(HttpMethod.POST.name, endpoint, response=response)

    def head(
        self, endpoint: str, /, *, response: Optional[Callable] = None
    ) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
        return self.request(HttpMethod.HEAD.name, endpoint, response=response)

    def patch(
        self, endpoint: str, /, *, response: Optional[Callable] = None
    ) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
        return self.request(HttpMethod.PATCH.name, endpoint, response=response)

    def delete(
        self, endpoint: str, /, *, response: Optional[Callable] = None
    ) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
        return self.request(HttpMethod.DELETE.name, endpoint, response=response)

    def options(
        self, endpoint: str, /, *, response: Optional[Callable] = None
    ) -> Callable[[Callable[PS, RT]], Callable[PS, RT]]:
        return self.request(HttpMethod.OPTIONS.name, endpoint, response=response)


class NeoClient(Client):
    def __init__(
        self,
        base_url: URLTypes = DEFAULT_BASE_URL,
        *,
        auth: Optional[AuthTypes] = DEFAULT_AUTH,
        params: Optional[QueriesTypes] = DEFAULT_PARAMS,
        headers: Optional[HeadersTypes] = DEFAULT_HEADERS,
        cookies: Optional[CookiesTypes] = DEFAULT_COOKIES,
        timeout: TimeoutTypes = DEFAULT_TIMEOUT,
        follow_redirects: bool = DEFAULT_FOLLOW_REDIRECTS,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        event_hooks: Optional[EventHooks] = DEFAULT_EVENT_HOOKS,
        trust_env: bool = DEFAULT_TRUST_ENV,
        default_encoding: DefaultEncodingTypes = DEFAULT_ENCODING,
        middleware: Optional[Sequence[MiddlewareCallable[Request, Response]]] = None,
    ) -> None:
        super().__init__(
            client=Session(
                auth=auth,
                params=params,
                headers=headers,
                cookies=cookies,
                timeout=timeout,
                follow_redirects=follow_redirects,
                max_redirects=max_redirects,
                event_hooks=event_hooks,
                base_url=base_url,
                trust_env=trust_env,
                default_encoding=default_encoding,
            ),
            middleware=(
                Middleware(record=Record(middleware))
                if middleware is not None
                else Middleware()
            ),
        )
