import abc
import functools
import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union

import httpx
from httpx._config import DEFAULT_MAX_REDIRECTS, DEFAULT_TIMEOUT_CONFIG
from param.sentinels import Missing, MissingType
from typing_extensions import ParamSpec

from . import api
from .enums import HttpMethod
from .errors import NotAnOperation
from .models import ClientOptions, OperationSpecification, RequestOptions
from .operations import Operation, get_operation, has_operation
from .types import (
    AuthTypes,
    CookieTypes,
    DefaultEncodingTypes,
    EventHooks,
    HeaderTypes,
    QueryParamTypes,
    TimeoutTypes,
    URLTypes,
)

T = TypeVar("T")

PS = ParamSpec("PS")
RT = TypeVar("RT")


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
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
        follow_redirects: bool = False,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        event_hooks: Optional[EventHooks] = None,
        trust_env: bool = True,
        default_encoding: DefaultEncodingTypes = "utf-8",
        client: Union[None, httpx.Client, MissingType] = Missing,
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

        if client is Missing:
            self.client = client_options.build()
        else:
            if not client_options.is_default():
                raise Exception(
                    "Cannot specify both `client` and other config options."
                )

            self.client = client

    def create(self, protocol: Type[T], /) -> T:
        operations: Dict[str, Callable] = {
            member_name: member
            for member_name, member in inspect.getmembers(protocol)
            if has_operation(member)
        }

        attributes: dict = {"__module__": protocol.__module__}

        func: Callable
        for func in operations.values():
            attributes[func.__name__] = self.bind(func)

        return type(protocol.__name__, (BaseService,), attributes)()

    def _wrap(self, operation: Operation[PS, RT], /) -> Callable[PS, RT]:
        @functools.wraps(operation.func)
        def wrapper(*args: PS.args, **kwargs: PS.kwargs) -> RT:
            return operation(*args, **kwargs)

        setattr(wrapper, "operation", operation)

        return abc.abstractmethod(wrapper)

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
            # Assert params are valid
            api.get_params(func, request=specification.request)

            operation: Operation[PS, RT] = Operation(func, specification, self.client)

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
