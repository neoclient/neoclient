from typing import Any, Callable, List, Mapping, Sequence, Tuple, Union

from httpx import QueryParams
from httpx._types import (
    AsyncByteStream,
    AuthTypes,  # QueryParamTypes,
    CertTypes,
    CookieTypes,
    HeaderTypes,
    PrimitiveData,
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

QueryParamTypes: TypeAlias = Union[
    QueryParams,
    Mapping[str, Union[PrimitiveData, Sequence[PrimitiveData]]],
    List[Tuple[str, PrimitiveData]],
    Tuple[Tuple[str, PrimitiveData], ...],
    str,
    bytes,
]

MethodTypes: TypeAlias = Union[str, bytes]
JsonTypes: TypeAlias = Any
StreamTypes: TypeAlias = Union[SyncByteStream, AsyncByteStream]
EventHooks: TypeAlias = Mapping[str, List[Callable]]
DefaultEncodingTypes: TypeAlias = Union[str, Callable[[bytes], str]]
EventHook: TypeAlias = Callable[..., Any]

PathParamTypes: TypeAlias = Mapping[str, Any]
