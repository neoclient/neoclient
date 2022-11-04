import functools
import inspect
from dataclasses import dataclass
from enum import Enum, auto
from types import FunctionType, MethodType
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union

import httpx
from httpx._config import DEFAULT_MAX_REDIRECTS, DEFAULT_TIMEOUT_CONFIG
from loguru import logger
from typing_extensions import ParamSpec

from . import __version__
from .composition.api import get_fields
from .enums import HttpMethod
from .models import ClientOptions, OperationSpecification, RequestOptions
from .operations import CallableWithOperation, Operation
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


class MethodKind(Enum):
    METHOD = auto()
    CLASS_METHOD = auto()
    STATIC_METHOD = auto()


T = TypeVar("T")

PS = ParamSpec("PS")
RT = TypeVar("RT")


def get_method_kind(method: Union[FunctionType, MethodType, Callable], /) -> MethodKind:
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


@dataclass(init=False)
class FastClient:
    client: Optional[httpx.Client]

    def __init__(
        self,
        base_url: URLTypes = "",
        *,
        auth: Optional[AuthTypes] = None,
        params: Optional[QueriesTypes] = None,
        headers: Optional[HeadersTypes] = None,
        cookies: Optional[CookiesTypes] = None,
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

        client_options.headers.setdefault("user-agent", f"fastclient/{__version__}")

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
            if isinstance(member, CallableWithOperation)
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
            if not isinstance(member, CallableWithOperation):
                continue

            bound_member: CallableWithOperation = self.bind(member)
            bound_member_callable: Callable = bound_member

            method_kind: MethodKind = get_method_kind(member)

            if method_kind is MethodKind.METHOD:
                bound_member = bound_member_callable.__get__(obj)
            elif method_kind is MethodKind.CLASS_METHOD:
                bound_member = bound_member_callable.__get__(typ)

            operation: Operation = bound_member.operation

            operation.func = bound_member

            setattr(obj, member_name, bound_member)

        return obj

    def _wrap(self, operation: Operation[PS, RT], /) -> CallableWithOperation[PS, RT]:
        @functools.wraps(operation.func)
        def wrapper(*args: PS.args, **kwargs: PS.kwargs) -> RT:
            if inspect.ismethod(operation.func):
                # Read off `self` or `cls`
                _, *args = args  # type: ignore

            return operation(*args, **kwargs)

        operation.func = wrapper

        return wrapper

    def bind(
        self, func: CallableWithOperation[PS, RT], /
    ) -> CallableWithOperation[PS, RT]:
        operation: Operation[PS, RT] = func.operation

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
    ) -> Callable[[Callable[PS, RT]], CallableWithOperation[PS, RT]]:
        specification: OperationSpecification = OperationSpecification(
            request=RequestOptions(
                method=method,
                url=endpoint,
            ),
            response=response,
        )

        def decorator(func: Callable[PS, RT], /) -> CallableWithOperation[PS, RT]:
            logger.info(f"Creating operation: {method=} {endpoint=} {func=}")

            operation: Operation[PS, RT] = Operation(func, specification, self.client)

            logger.info(f"Created operation: {operation!r}")

            wrapped_func: CallableWithOperation[PS, RT] = self._wrap(operation)

            # Assert params are valid
            get_fields(operation.specification.request, wrapped_func)

            return wrapped_func

        return decorator

    def put(
        self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
    ) -> Callable[[Callable[PS, RT]], CallableWithOperation[PS, RT]]:
        return self.request(HttpMethod.PUT.name, endpoint, response=response)

    def get(
        self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
    ) -> Callable[[Callable[PS, RT]], CallableWithOperation[PS, RT]]:
        return self.request(HttpMethod.GET.name, endpoint, response=response)

    def post(
        self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
    ) -> Callable[[Callable[PS, RT]], CallableWithOperation[PS, RT]]:
        return self.request(HttpMethod.POST.name, endpoint, response=response)

    def head(
        self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
    ) -> Callable[[Callable[PS, RT]], CallableWithOperation[PS, RT]]:
        return self.request(HttpMethod.HEAD.name, endpoint, response=response)

    def patch(
        self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
    ) -> Callable[[Callable[PS, RT]], CallableWithOperation[PS, RT]]:
        return self.request(HttpMethod.PATCH.name, endpoint, response=response)

    def delete(
        self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
    ) -> Callable[[Callable[PS, RT]], CallableWithOperation[PS, RT]]:
        return self.request(HttpMethod.DELETE.name, endpoint, response=response)

    def options(
        self, endpoint: str, /, *, response: Optional[Callable[..., Any]] = None
    ) -> Callable[[Callable[PS, RT]], CallableWithOperation[PS, RT]]:
        return self.request(HttpMethod.OPTIONS.name, endpoint, response=response)
