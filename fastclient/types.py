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
    RequestFiles,
    SyncByteStream,
    TimeoutTypes,
    URLTypes,
    VerifyTypes,
)
from typing_extensions import TypeAlias

StrOrBytes = TypeVar("StrOrBytes", str, bytes)

Primitive: TypeAlias = Union[
    str,
    int,
    float,
    bool,
    None,
]
QueryTypes: TypeAlias = Any
HeaderTypes: TypeAlias = Any
CookieTypes: TypeAlias = Any
PathTypes: TypeAlias = Union[Primitive, Sequence[Primitive]]
QueriesTypes: TypeAlias = Union[
    QueryParams,
    Mapping[str, Union[Primitive, Sequence[Primitive]]],
    Sequence[Tuple[str, Primitive]],
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
PathsTypes: TypeAlias = Mapping[str, PathTypes]

MethodTypes: TypeAlias = Union[str, bytes]
JsonTypes: TypeAlias = Any
StreamTypes: TypeAlias = Union[SyncByteStream, AsyncByteStream]
EventHooks: TypeAlias = Mapping[str, List[Callable]]
DefaultEncodingTypes: TypeAlias = Union[str, Callable[[bytes], str]]
EventHook: TypeAlias = Callable[..., Any]
