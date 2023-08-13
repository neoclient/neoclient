from http.cookiejar import CookieJar
from typing import Any, Callable, List, Mapping, Sequence, Tuple, TypeVar, Union

from httpx import Cookies, Headers, QueryParams
from httpx._types import (
    AsyncByteStream,
    AuthTypes,
    CertTypes,
    ProxiesTypes,
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
from typing_extensions import TypeAlias

__all__: Sequence[str] = (
    "AuthTypes",
    "CertTypes",
    "ProxiesTypes",
    "RequestContent",
    "RequestData",
    "RequestExtensions",
    "RequestFiles",
    "ResponseContent",
    "ResponseExtensions",
    "TimeoutTypes",
    "URLTypes",
    "VerifyTypes",
    "Primitive",
    "QueryTypes",
    "HeaderTypes",
    "CookieTypes",
    "PathTypes",
    "QueriesTypes",
    "HeadersTypes",
    "CookiesTypes",
    "PathsTypes",
    "MethodTypes",
    "JsonTypes",
    "StreamTypes",
    "EventHook",
    "EventHooks",
    "DefaultEncodingTypes",
)

StrOrBytes = TypeVar("StrOrBytes", str, bytes)

Primitive: TypeAlias = Union[
    str,
    int,
    float,
    bool,
    None,
]
QueryTypes: TypeAlias = Any
HeaderTypes: TypeAlias = Union[Primitive, Sequence[Primitive]]
CookieTypes: TypeAlias = Any
PathTypes: TypeAlias = Union[Primitive, Sequence[Primitive]]
QueriesTypes: TypeAlias = Union[
    QueryParams,
    Mapping[str, Union[Primitive, Sequence[Primitive]]],
    Sequence[Tuple[str, Primitive]],
    Sequence[str],
    str,
    bytes,
]
HeadersTypes: TypeAlias = Union[
    Headers,
    Mapping[StrOrBytes, StrOrBytes],
    Sequence[Tuple[StrOrBytes, StrOrBytes]],
]
CookiesTypes: TypeAlias = Union[
    Cookies,
    CookieJar,
    Mapping[str, str],
    Sequence[Tuple[str, str]],
]
PathsTypes: TypeAlias = Union[
    Mapping[str, PathTypes],
    Sequence[Tuple[str, PathTypes]],
]

MethodTypes: TypeAlias = Union[str, bytes]
JsonTypes: TypeAlias = Any
StreamTypes: TypeAlias = Union[SyncByteStream, AsyncByteStream]
EventHook: TypeAlias = Callable[..., Any]
EventHooks: TypeAlias = Mapping[str, List[EventHook]]
DefaultEncodingTypes: TypeAlias = Union[str, Callable[[bytes], str]]
