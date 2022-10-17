from enum import Enum, auto
import functools
import inspect
from dataclasses import dataclass, field
from types import FunctionType, MethodType
from typing import Any, Callable, Dict, List, Mapping, Optional, Type, TypeVar, Union

from loguru import logger
import httpx
from httpx import QueryParams, Headers, Cookies, Timeout, URL
from httpx._auth import Auth
from httpx._config import (
    DEFAULT_MAX_REDIRECTS,
    DEFAULT_TIMEOUT_CONFIG,
    DEFAULT_LIMITS,
    Limits,
)
from httpx._transports.base import BaseTransport
from typing_extensions import ParamSpec

from .enums import HttpMethod
from .models import ClientOptions, OperationSpecification, RequestOptions
from .operations import Operation, get_operation, has_operation, set_operation
from .types import (
    AuthTypes,
    CookieTypes,
    DefaultEncodingTypes,
    EventHooks,
    HeaderTypes,
    QueryParamTypes,
    TimeoutTypes,
    URLTypes,
    VerifyTypes,
    CertTypes,
    ProxiesTypes,
    EventHook,
)


class MethodKind(Enum):
    METHOD = auto()
    CLASS_METHOD = auto()
    STATIC_METHOD = auto()


T = TypeVar("T")

PS = ParamSpec("PS")
RT = TypeVar("RT")


def get_method_kind(method: Union[FunctionType, MethodType], /) -> MethodKind:
    if isinstance(method, MethodType):
        if isinstance(method.__self__, type):
            return MethodKind.CLASS_METHOD
        else:
            return MethodKind.METHOD
    elif isinstance(method, FunctionType):
        return MethodKind.STATIC_METHOD
    else:
        raise ValueError(
            "`method` is not a function or method, cannot determine its kind"
        )


class BaseService:
    def __repr__(self) -> str:
        return f"<{type(self).__name__}()>"


# @dataclass(init=False)
# class Client(httpx.Client):
#     auth: Optional[Auth]
#     params: QueryParams
#     headers: Headers
#     cookies: Cookies
#     timeout: Timeout
#     follow_redirects: bool
#     max_redirects: int
#     event_hooks: Dict[str, List[Callable]]
#     base_url: URL
#     trust_env: bool

# auth: Optional[Auth] = None
# params: QueryParams = field(default_factory=QueryParams)
# headers: Headers = field(default_factory=lambda: Headers({'accept': '*/*', 'accept-encoding': 'gzip, deflate, br', 'connection': 'keep-alive', 'user-agent': 'python-httpx/0.23.0'}))
# cookies: Cookies = field(default_factory=Cookies)
# timeout: Timeout = DEFAULT_TIMEOUT_CONFIG
# follow_redirects: bool = False
# max_redirects: int = DEFAULT_MAX_REDIRECTS
# event_hooks: Dict[str, List[Callable]] = field(default_factory=lambda: {'request': [], 'response': []})
# base_url: URL = field(default_factory=URL)
# trust_env: bool = True

# def __init__(
#     self,
#     *,
#     auth: Optional[AuthTypes] = None,
#     params: Optional[QueryParamTypes] = None,
#     headers: Optional[HeaderTypes] = None,
#     cookies: Optional[CookieTypes] = None,
#     verify: VerifyTypes = True,
#     cert: Optional[CertTypes] = None,
#     http1: bool = True,
#     http2: bool = False,
#     proxies: Optional[ProxiesTypes] = None,
#     mounts: Optional[Mapping[str, BaseTransport]] = None,
#     timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
#     follow_redirects: bool = False,
#     limits: Limits = DEFAULT_LIMITS,
#     max_redirects: int = DEFAULT_MAX_REDIRECTS,
#     event_hooks: Optional[
#         Mapping[str, List[EventHook]]
#     ] = None,
#     base_url: URLTypes = "",
#     transport: Optional[BaseTransport] = None,
#     app: Optional[Callable[..., Any]] = None,
#     trust_env: bool = True,
#     default_encoding: Union[str, Callable[[bytes], str]] = "utf-8",
# ):


@dataclass(init=False)
class FastClient:
    client: Optional[httpx.Client]

    def __init__(
        self,
        base_url: URLTypes = "",
        *,
        auth: Optional[AuthTypes] = None,
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
        follow_redirects: bool = False,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        event_hooks: Optional[EventHooks] = None,
        trust_env: bool = True,
        default_encoding: DefaultEncodingTypes = "utf-8",
    ) -> None:
        client_options: ClientOptions = ClientOptions(
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

        self.client = client_options.build()

    @classmethod
    def from_client(cls, client: Optional[httpx.Client], /) -> "FastClient":
        obj = cls()

        obj.client = client

        return obj

    def create(self, protocol: Type[T], /) -> T:
        operations: Dict[str, Callable] = {
            member_name: member
            for member_name, member in inspect.getmembers(protocol)
            if has_operation(member)
        }

        attributes: dict = {"__module__": protocol.__module__}

        func: Callable
        for func in operations.values():
            static_attr = inspect.getattr_static(protocol, func.__name__)

            attributes[func.__name__] = static_attr

        typ = type(protocol.__name__, (BaseService,), attributes)
        obj = typ()

        member_name: str
        member: Any
        for member_name, member in inspect.getmembers(obj):
            if not has_operation(member):
                continue

            bound_member = self.bind(member)

            method_kind: MethodKind = get_method_kind(member)

            if method_kind is MethodKind.METHOD:
                bound_member = bound_member.__get__(obj)
            elif method_kind is MethodKind.CLASS_METHOD:
                bound_member = bound_member.__get__(typ)

            operation: Operation = get_operation(bound_member)

            operation.func = bound_member

            setattr(obj, member_name, bound_member)

        return obj

    def _wrap(self, operation: Operation[PS, RT], /) -> Callable[PS, RT]:
        @functools.wraps(operation.func)
        def wrapper(*args: PS.args, **kwargs: PS.kwargs) -> RT:
            if inspect.ismethod(operation.func):
                # Read off `self` or `cls`
                _, *args = args  # type: ignore

            return operation(*args, **kwargs)

        operation.func = wrapper

        set_operation(wrapper, operation)

        return wrapper

    def bind(self, func: Callable[PS, RT], /) -> Callable[PS, RT]:
        operation: Operation[PS, RT] = get_operation(func)

        bound_operation: Operation[PS, RT] = Operation(
            operation.func, operation.specification, self.client
        )

        return self._wrap(bound_operation)

    def request(
        self,
        method: str,
        endpoint: str,
        /,
        *,
        response: Optional[Callable[..., Any]] = None,
    ):
        specification: OperationSpecification = OperationSpecification(
            request=RequestOptions(
                method=method,
                url=endpoint,
            ),
            response=response,
        )

        def decorator(func: Callable[PS, RT], /) -> Callable[PS, RT]:
            logger.info(f"Creating operation: {method=} {endpoint=} {func=}")

            # Assert params are valid
            # NOTE: Temporarily disabled whilst `api` being deprecated
            # api.get_params(func, request=specification.request)

            operation: Operation[PS, RT] = Operation(func, specification, self.client)

            logger.info(f"Created operation: {operation!r}")

            return self._wrap(operation)

        return decorator

    def put(self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None):
        return self.request(HttpMethod.PUT.name, endpoint, response=response)

    def get(self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None):
        return self.request(HttpMethod.GET.name, endpoint, response=response)

    def post(self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None):
        return self.request(HttpMethod.POST.name, endpoint, response=response)

    def head(self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None):
        return self.request(HttpMethod.HEAD.name, endpoint, response=response)

    def patch(self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None):
        return self.request(HttpMethod.PATCH.name, endpoint, response=response)

    def delete(
        self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
    ):
        return self.request(HttpMethod.DELETE.name, endpoint, response=response)

    def options(
        self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
    ):
        return self.request(HttpMethod.OPTIONS.name, endpoint, response=response)
