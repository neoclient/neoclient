# from typing import Dict, Sequence, Tuple, Union, Mapping, List, Any
from typing import Any, Callable, List, Mapping, Union

from httpx._types import (
    AsyncByteStream,
    AuthTypes,
    CookieTypes,
    HeaderTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestFiles,
    SyncByteStream,
    TimeoutTypes,
    URLTypes,
)
from typing_extensions import TypeAlias

# from httpx import Headers, Timeout, URL, QueryParams, Cookies
# from http.cookiejar import CookieJar

# HeadersType: TypeAlias = Union[
#     Headers,
#     Dict[str, str],
#     Dict[bytes, bytes],
#     Sequence[Tuple[str, str]],
#     Sequence[Tuple[bytes, bytes]],
#     None,
# ]

# TimeoutType: TypeAlias = Union[float, Timeout, None]

MethodTypes: TypeAlias = Union[str, bytes]
# UrlType: TypeAlias = Union[URL, str, Tuple[bytes, bytes, Union[int, None], bytes]]
# ParamsType: TypeAlias = Union[
#     QueryParams,
#     Mapping[
#         str,
#         Union[
#             str, int, float, bool, None, Sequence[Union[str, int, float, bool, None]]
#         ],
#     ],
#     List[Tuple[str, Union[str, int, float, bool, None]]],
#     Tuple[Tuple[str, Union[str, int, float, bool, None]], ...],
#     str,
#     bytes,
#     None,
# ]
JsonTypes: TypeAlias = Any
# CookiesType: TypeAlias = Union[Cookies, CookieJar, Dict[str, str], List[Tuple[str, str]], None]
StreamTypes: TypeAlias = Union[SyncByteStream, AsyncByteStream]
EventHooks: TypeAlias = Mapping[str, List[Callable]]
DefaultEncodingTypes: TypeAlias = Union[str, Callable[[bytes], str]]