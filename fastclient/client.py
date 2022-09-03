import abc
import functools
from typing import (
    Any,
    Callable,
    Dict,
    List,
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

from . import api, methods
from .enums import HttpMethod
from .models import ClientOptions
from .operations import Operation, BoundOperation, get_operation
from .params import Path

T = TypeVar("T")

PT = ParamSpec("PT")
RT = TypeVar("RT")


class BaseService:
    def __repr__(self) -> str:
        return f"<{type(self).__name__}()>"


class FastClient:
    _client_options: ClientOptions
    _client: Optional[httpx.Client]

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

        self._client_options = ClientOptions(
            base_url=base_url,
            headers=headers,
        )

        if client is Missing:
            self._client = self._client_options.build()
        elif client is None:
            if not self._client_options.is_default():
                raise Exception(
                    "Cannot specify both `client` and other config options."
                )

            self._client = None
        else:
            self._client = client

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            return self._client_options.build()

        return self._client

    def __repr__(self) -> str:
        return f"{type(self).__name__}(client={self.client!r})"

    def create(self, protocol: Type[T], /) -> T:
        operations: Dict[str, Callable] = api.get_operations(protocol)

        attributes: dict = {"__module__": protocol.__module__}

        method: Callable
        for method in operations.values():
            operation.bind(self.client)

            attributes[operation.func.__name__] = functools.wraps(operation.func)(
                bound_operation
            )

        return type(protocol.__name__, (BaseService,), attributes)()

    def bind(self, func: Callable[PT, RT], /) -> Callable[PT, RT]:
        operation: Optional[Operation] = get_operation(func)

        if operation is None:
            raise Exception("Cannot bind client to non-operation")

        if isinstance(operation, BoundOperation):
            raise Exception("Operation has already been bound")

        bound_operation: BoundOperation = BoundOperation(operation.func, operation.specification, client=self.client)

        @functools.wraps(func)
        def wrapper(*args: PT.args, **kwargs: PT.kwargs) -> RT:
            return bound_operation(*args, **kwargs)

        setattr(wrapper, "operation", bound_operation)

        return wrapper

    def request(
        self,
        method: str,
        endpoint: Optional[str] = None,
        /,
        *,
        response: Optional[Callable[..., Any]] = None,
    ):
        def decorator(func: Callable[PT, RT], /) -> Callable[PT, RT]:
            uri: str = (
                endpoint if endpoint is not None else Path.generate_alias(func.__name__)
            )

            unbound_func: Callable[PT, RT] = methods.request(method, uri, response=response)(func)

            return self.bind(unbound_func)

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
