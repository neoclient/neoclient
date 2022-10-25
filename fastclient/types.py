from typing import Any, Callable, List, Mapping, Sequence, Tuple, Union

from httpx._types import (
    AsyncByteStream,
    AuthTypes,
    CookieTypes,
    HeaderTypes,
    # QueryParamTypes,
    RequestContent,
    RequestData,
    RequestFiles,
    SyncByteStream,
    TimeoutTypes,
    URLTypes,
    VerifyTypes,
    CertTypes,
    ProxiesTypes,
    PrimitiveData,
)
from httpx import QueryParams
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