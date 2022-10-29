from typing import (
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    Sequence,
    Tuple,
    Union,
)
from http.cookiejar import CookieJar

from httpx import (
    QueryParams,
    Headers,
    Cookies,
)
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

Primitive: TypeAlias = Union[
    str,
    int,
    float,
    bool,
    None,
]

QueryParamTypes: TypeAlias = Union[
    QueryParams,
    Mapping[str, Union[Primitive, Sequence[Primitive]]],
    List[Tuple[str, Primitive]],
    Tuple[Tuple[str, Primitive], ...],
    str,
    bytes,
]

HeaderTypes: TypeAlias = Union[
    Headers,
    Mapping[str, str],
    Mapping[bytes, bytes],
    Sequence[Tuple[str, str]],
    Sequence[Tuple[bytes, bytes]],
]

CookieTypes: TypeAlias = Union[
    Cookies,
    CookieJar,
    Dict[str, str],
    List[Tuple[str, str]],
]

MethodTypes: TypeAlias = Union[str, bytes]
JsonTypes: TypeAlias = Any
StreamTypes: TypeAlias = Union[SyncByteStream, AsyncByteStream]
EventHooks: TypeAlias = Mapping[str, List[Callable]]
DefaultEncodingTypes: TypeAlias = Union[str, Callable[[bytes], str]]
EventHook: TypeAlias = Callable[..., Any]

PathParamValueTypes: TypeAlias = Union[Primitive, Sequence[Primitive]]
PathParamTypes: TypeAlias = Mapping[str, PathParamValueTypes]