import abc
import functools
from typing import (
    Any,
    Callable,
    Dict,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
)

import httpx
from param.sentinels import Missing, MissingType
from typing_extensions import ParamSpec

from . import api
from .enums import HttpMethod
from .models import ClientOptions, OperationSpecification
from .operations import Operation, get_operation

T = TypeVar("T")

PS = ParamSpec("PS")
RT = TypeVar("RT")


class BaseService:
    def __repr__(self) -> str:
        return f"<{type(self).__name__}()>"


class FastClient:
    client: Optional[httpx.Client]

    def __init__(
        self,
        base_url: Union[httpx.URL, str] = "",
        *,
        client: Union[None, httpx.Client, MissingType] = Missing,
        headers: Union[
            httpx.Headers,
            Dict[str, str],
            Dict[bytes, bytes],
            Sequence[Tuple[str, str]],
            Sequence[Tuple[bytes, bytes]],
            None,
        ] = None,
    ) -> None:
        # TODO: Add other named params and use proper types beyond just `headers`

        client_options: ClientOptions = ClientOptions(
            base_url=base_url,
            headers=headers,
        )

        if client is Missing:
            self.client = client_options.build()
        else:
            if not client_options.is_default():
                raise Exception(
                    "Cannot specify both `client` and other config options."
                )

            self.client = client

    def __repr__(self) -> str:
        return f"{type(self).__name__}(client={self.client!r})"

    def create(self, protocol: Type[T], /) -> T:
        operations: Dict[str, Callable] = api.get_operations(protocol)

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
        operation: Optional[Operation[PS, RT]] = get_operation(func)

        if operation is None:
            raise Exception("Cannot bind client to non-operation")

        bound_operation: Operation[PS, RT] = Operation(operation.func, operation.specification, self.client)

        return self._wrap(bound_operation)

    def request(
        self,
        method: str,
        endpoint: str,
        /,
        *,
        response: Optional[Callable[..., Any]] = None,
    ):
        def decorator(func: Callable[PS, RT], /) -> Callable[PS, RT]:
            specification: OperationSpecification = api.build_request_specification(
                func, method, endpoint, response=response
            )

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
