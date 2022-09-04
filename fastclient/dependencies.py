from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Dict, List, Optional

import httpx

from .parameter_functions import Cookies, Headers, Promise
from .types import StreamTypes


@dataclass
class HeaderResponse:
    name: str

    def __call__(self, headers: httpx.Headers = Headers()) -> str:
        return headers[self.name]


@dataclass
class CookieResponse:
    name: str

    def __call__(self, cookies: httpx.Cookies = Cookies()) -> str:
        return cookies[self.name]


def charset_encoding(response: httpx.Response = Promise()) -> Optional[str]:
    return response.charset_encoding


def content(response: httpx.Response = Promise()) -> bytes:
    return response.content


def cookies(response: httpx.Response = Promise()) -> httpx.Cookies:
    return response.cookies


def elapsed(response: httpx.Response = Promise()) -> timedelta:
    return response.elapsed


def encoding(response: httpx.Response = Promise()) -> Optional[str]:
    return response.encoding


def has_redirect_location(response: httpx.Response = Promise()) -> bool:
    return response.has_redirect_location


def headers(response: httpx.Response = Promise()) -> httpx.Headers:
    return response.headers


def history(response: httpx.Response = Promise()) -> List[httpx.Response]:
    return response.history


def http_version(response: httpx.Response = Promise()) -> str:
    return response.http_version


def is_client_error(response: httpx.Response = Promise()) -> bool:
    return response.is_client_error


def is_closed(response: httpx.Response = Promise()) -> bool:
    return response.is_closed


def is_error(response: httpx.Response = Promise()) -> bool:
    return response.is_error


def is_informational(response: httpx.Response = Promise()) -> bool:
    return response.is_informational


def is_redirect(response: httpx.Response = Promise()) -> bool:
    return response.is_redirect


def is_server_error(response: httpx.Response = Promise()) -> bool:
    return response.is_server_error


def is_stream_consumed(response: httpx.Response = Promise()) -> bool:
    return response.is_stream_consumed


def is_success(response: httpx.Response = Promise()) -> bool:
    return response.is_success


def json(response: httpx.Response = Promise()) -> Any:
    return response.json()


def links(response: httpx.Response = Promise()) -> Dict[Optional[str], Dict[str, str]]:
    return response.links


def next_request(response: httpx.Response = Promise()) -> Optional[httpx.Request]:
    return response.next_request


def num_bytes_downloaded(response: httpx.Response = Promise()) -> int:
    return response.num_bytes_downloaded


def reason_phrase(response: httpx.Response = Promise()) -> str:
    return response.reason_phrase


def request(response: httpx.Response = Promise()) -> httpx.Request:
    return response.request


def status_code(response: httpx.Response = Promise()) -> int:
    return response.status_code


def stream(response: httpx.Response = Promise()) -> StreamTypes:
    return response.stream


def text(response: httpx.Response = Promise()) -> str:
    return response.text


def url(response: httpx.Response = Promise()) -> httpx.URL:
    return response.url


def request_content(request: httpx.Request = Promise()) -> bytes:
    return request.content


def request_headers(request: httpx.Request = Promise()) -> httpx.Headers:
    return request.headers


def request_method(request: httpx.Request = Promise()) -> str:
    return request.method


def request_stream(request: httpx.Request = Promise()) -> StreamTypes:
    return request.stream


def request_url(request: httpx.Request = Promise()) -> httpx.URL:
    return request.url
