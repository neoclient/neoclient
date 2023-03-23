import datetime
from http import HTTPStatus
from typing import Mapping, MutableSequence, Tuple

from httpx import Cookies, Request, Response


def test_charset_encoding() -> None:
    charset_encoding: str = "foo"

    response: Response = Response(
        HTTPStatus.OK,
        headers={"Content-Type": f"text/plain;charset={charset_encoding}"},
    )

    assert response.charset_encoding == charset_encoding


def test_content() -> None:
    content: bytes = b"foo"

    response: Response = Response(HTTPStatus.OK, content=content)

    assert response.content == content


def test_cookies() -> None:
    domain: str = "foo.bar"
    path: str = "/"
    cookies: Mapping[str, str] = {"x-foo": "foo", "x-bar": "bar"}

    response_headers: MutableSequence[Tuple[str, str]] = []
    expected_cookies: Cookies = Cookies()

    cookie_name: str
    cookie_value: str
    for cookie_name, cookie_value in cookies.items():
        response_headers.append(("Set-Cookie", f"{cookie_name}={cookie_value}"))
        expected_cookies.set(cookie_name, cookie_value, domain=domain, path=path)

    response: Response = Response(
        HTTPStatus.OK,
        request=Request("GET", f"https://{domain}/"),
        headers=response_headers,
    )

    assert response.cookies == expected_cookies


def test_elapsed() -> None:
    elapsed: datetime.timedelta = datetime.timedelta(seconds=32)

    response: Response = Response(HTTPStatus.OK)

    response.elapsed = elapsed

    assert response.elapsed == elapsed


def test_encoding() -> None:
    encoding: str = "foo"

    response: Response = Response(HTTPStatus.OK, default_encoding=encoding)

    assert response.encoding == encoding


def test_has_redirect_location() -> None:
    ...


def test_headers() -> None:
    ...


def test_history() -> None:
    ...


def test_http_version() -> None:
    ...


def test_is_client_error() -> None:
    ...


def test_is_closed() -> None:
    ...


def test_is_error() -> None:
    ...


def test_is_informational() -> None:
    ...


def test_is_redirect() -> None:
    ...


def test_is_server_error() -> None:
    ...


def test_is_stream_consumed() -> None:
    ...


def test_is_success() -> None:
    ...


def test_json() -> None:
    ...


def test_links() -> None:
    ...


def test_next_request() -> None:
    ...


def test_num_bytes_downloaded() -> None:
    ...


def test_reason_phrase() -> None:
    ...


def test_request() -> None:
    ...


def test_response() -> None:
    ...


def test_status_code() -> None:
    ...


def test_stream() -> None:
    ...


def test_text() -> None:
    ...


def test_url() -> None:
    ...


def test_request_content() -> None:
    ...


def test_request_headers() -> None:
    ...


def test_request_method() -> None:
    ...


def test_request_params() -> None:
    ...


def test_request_stream() -> None:
    ...


def test_request_url() -> None:
    ...
