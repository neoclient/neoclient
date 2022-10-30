from http.cookiejar import CookieJar
from typing import Any, Callable, Dict, List, Mapping, Sequence, Tuple, Union

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

# NOTE: In an upcoming release of `httpx` (> 0.23.0), `Dict` should be replaced by `Mapping`
# Once this version is released, the dependency should be bumped and the types should be
# updated here accordingly
HeaderTypes: TypeAlias = Union[
    Headers,
    Dict[str, str],
    Dict[bytes, bytes],
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
