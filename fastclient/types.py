from typing import Dict, Sequence, Tuple, Union, Mapping, List, Any
from typing_extensions import TypeAlias
from httpx import Headers, Timeout, URL, QueryParams, Cookies
from http.cookiejar import CookieJar

HeadersType: TypeAlias = Union[
    Headers,
    Dict[str, str],
    Dict[bytes, bytes],
    Sequence[Tuple[str, str]],
    Sequence[Tuple[bytes, bytes]],
    None,
]

TimeoutType: TypeAlias = Union[float, Timeout, None]

MethodType: TypeAlias = Union[str, bytes]
UrlType: TypeAlias = Union[URL, str, Tuple[bytes, bytes, Union[int, None], bytes]]
ParamsType: TypeAlias = Union[
    QueryParams,
    Mapping[
        str,
        Union[
            str, int, float, bool, None, Sequence[Union[str, int, float, bool, None]]
        ],
    ],
    List[Tuple[str, Union[str, int, float, bool, None]]],
    Tuple[Tuple[str, Union[str, int, float, bool, None]], ...],
    str,
    bytes,
    None,
]
JsonType: TypeAlias = Union[Any, None]
CookiesType: TypeAlias = Union[Cookies, CookieJar, Dict[str, str], List[Tuple[str, str]], None]