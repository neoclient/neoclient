import httpx
from typing import Mapping

m1: Mapping[str, str] = httpx.Headers()
m2: Mapping[str, str] = httpx.Cookies()
m3: Mapping[str, str] = httpx.QueryParams()