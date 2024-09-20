from datetime import timedelta
from typing import Any, Dict, List, Optional

from httpx import URL, Cookies, Headers, QueryParams, Request, Response

from ..types import StreamTypes

__all__ = (
    "charset_encoding",
    "content",
    "cookies",
    "elapsed",
    "encoding",
    "has_redirect_location",
    "headers",
    "history",
    "http_version",
    "is_client_error",
    "is_closed",
    "is_error",
    "is_informational",
    "is_redirect",
    "is_server_error",
    "is_stream_consumed",
    "is_success",
    "json",
    "links",
    "next_request",
    "num_bytes_downloaded",
    "reason_phrase",
    "request",
    "response",
    "status_code",
    "stream",
    "text",
    "url",
    "request_content",
    "request_headers",
    "request_method",
    "request_params",
    "request_stream",
    "request_url",
)


def charset_encoding(response: Response) -> Optional[str]:
    return response.charset_encoding


def content(response: Response) -> bytes:
    return response.content


def cookies(response: Response) -> Cookies:
    return response.cookies


def elapsed(response: Response) -> timedelta:
    return response.elapsed


def encoding(response: Response) -> Optional[str]:
    return response.encoding


def has_redirect_location(response: Response) -> bool:
    return response.has_redirect_location


def headers(response: Response) -> Headers:
    return response.headers


def history(response: Response) -> List[Response]:
    return response.history


def http_version(response: Response) -> str:
    return response.http_version


def is_client_error(response: Response) -> bool:
    return response.is_client_error


def is_closed(response: Response) -> bool:
    return response.is_closed


def is_error(response: Response) -> bool:
    return response.is_error


def is_informational(response: Response) -> bool:
    return response.is_informational


def is_redirect(response: Response) -> bool:
    return response.is_redirect


def is_server_error(response: Response) -> bool:
    return response.is_server_error


def is_stream_consumed(response: Response) -> bool:
    return response.is_stream_consumed


def is_success(response: Response) -> bool:
    return response.is_success


def json(response: Response) -> Any:
    return response.json()


def links(response: Response) -> Dict[Optional[str], Dict[str, str]]:
    return response.links


def next_request(response: Response) -> Optional[Request]:
    return response.next_request


def num_bytes_downloaded(response: Response) -> int:
    return response.num_bytes_downloaded


def reason_phrase(response: Response) -> str:
    return response.reason_phrase


def request(response: Response) -> Request:
    return response.request


def response(response: Response) -> Response:
    return response


def status_code(response: Response) -> int:
    return response.status_code


def stream(response: Response) -> StreamTypes:
    return response.stream


def text(response: Response) -> str:
    return response.text


def url(response: Response) -> URL:
    return response.url


def request_content(request: Request) -> bytes:
    return request.content


def request_headers(request: Request) -> Headers:
    return request.headers


def request_method(request: Request) -> str:
    return request.method


def request_params(request: Request) -> QueryParams:
    return request.url.params


def request_stream(request: Request) -> StreamTypes:
    return request.stream


def request_url(request: Request) -> URL:
    return request.url
