import datetime
from http import HTTPStatus
from typing import Any, Dict, List, Mapping, MutableSequence, Sequence, Tuple

from httpx import (
    ByteStream,
    Cookies,
    Headers,
    QueryParams,
    Request,
    Response,
    SyncByteStream,
)

from neoclient import dependencies
from neoclient.enums import HTTPMethod


def test_charset_encoding() -> None:
    charset_encoding: str = "foo"

    response: Response = Response(
        HTTPStatus.OK,
        headers={"Content-Type": f"text/plain;charset={charset_encoding}"},
    )

    assert (
        dependencies.charset_encoding(response)
        == response.charset_encoding
        == charset_encoding
    )


def test_content() -> None:
    content: bytes = b"foo"

    response: Response = Response(HTTPStatus.OK, content=content)

    assert dependencies.content(response) == response.content == content


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
        request=Request(HTTPMethod.GET, f"https://{domain}/"),
        headers=response_headers,
    )

    assert dependencies.cookies(response) == response.cookies == expected_cookies


def test_elapsed() -> None:
    elapsed: datetime.timedelta = datetime.timedelta(seconds=32)

    response: Response = Response(HTTPStatus.OK)

    response.elapsed = elapsed

    assert dependencies.elapsed(response) == response.elapsed == elapsed


def test_encoding() -> None:
    encoding: str = "foo"

    response: Response = Response(HTTPStatus.OK, default_encoding=encoding)

    assert dependencies.encoding(response) == response.encoding == encoding


def test_has_redirect_location() -> None:
    response: Response = Response(
        HTTPStatus.SEE_OTHER, headers={"Location": "https://foo.bar/"}
    )

    assert (
        dependencies.has_redirect_location(response)
        == response.has_redirect_location
        is True
    )


def test_headers() -> None:
    headers: Headers = Headers({"x-foo": "foo", "x-bar": "bar"})

    response: Response = Response(HTTPStatus.OK, headers=headers)

    assert dependencies.headers(response) == response.headers == headers


def test_history() -> None:
    history: List[Response] = [
        Response(HTTPStatus.SEE_OTHER, headers={"Location": "https://foo.bar/"})
    ]

    response: Response = Response(HTTPStatus.OK, history=history)

    assert dependencies.history(response) == response.history == history


def test_http_version() -> None:
    http_version: str = "HTTP/9.9"

    response: Response = Response(
        HTTPStatus.OK, extensions={"http_version": http_version.encode()}
    )

    assert dependencies.http_version(response) == response.http_version == http_version


def test_is_client_error() -> None:
    response_not_client_error: Response = Response(HTTPStatus.OK)
    response_client_error: Response = Response(HTTPStatus.BAD_REQUEST)

    assert (
        dependencies.is_client_error(response_not_client_error)
        is response_not_client_error.is_client_error
        is False
    )
    assert (
        dependencies.is_client_error(response_client_error)
        is response_client_error.is_client_error
        is True
    )


def test_is_closed() -> None:
    response: Response = Response(HTTPStatus.OK, stream=ByteStream(b"foo"))

    assert dependencies.is_closed(response) is response.is_closed is False

    response.close()

    assert dependencies.is_closed(response) is response.is_closed is True


def test_is_error() -> None:
    response: Response = Response(HTTPStatus.INTERNAL_SERVER_ERROR)

    assert dependencies.is_error(response) is response.is_error is True


def test_is_informational() -> None:
    response: Response = Response(HTTPStatus.CONTINUE)

    assert dependencies.is_informational(response) is response.is_informational is True


def test_is_redirect() -> None:
    response: Response = Response(
        HTTPStatus.SEE_OTHER, headers={"Location": "https://foo.bar/"}
    )

    assert dependencies.is_redirect(response) is response.is_redirect is True


def test_is_server_error() -> None:
    response: Response = Response(HTTPStatus.INTERNAL_SERVER_ERROR)

    assert dependencies.is_server_error(response) is response.is_server_error is True


def test_is_stream_consumed() -> None:
    response: Response = Response(HTTPStatus.OK, stream=ByteStream(b"foo"))

    assert (
        dependencies.is_stream_consumed(response)
        is response.is_stream_consumed
        is False
    )

    response.read()

    assert (
        dependencies.is_stream_consumed(response) is response.is_stream_consumed is True
    )


def test_is_success() -> None:
    response_ok: Response = Response(HTTPStatus.OK)
    response_error: Response = Response(HTTPStatus.INTERNAL_SERVER_ERROR)

    assert dependencies.is_success(response_ok) is response_ok.is_success is True
    assert dependencies.is_success(response_error) is response_error.is_success is False


def test_json() -> None:
    json: Any = {"foo": "bar"}

    response: Response = Response(HTTPStatus.OK, json=json)

    assert dependencies.json(response) == response.json() == json


def test_links() -> None:
    links: Dict[str, Dict[str, str]] = {
        "https://example.com/": {
            "foo": "foo",
            "bar": "bar",
            "url": "https://example.com/",
        }
    }

    encoded_links: MutableSequence[str] = []

    url: str
    params: Dict[str, str]
    for url, params in links.items():
        link: str = f"<{url}>"

        encoded_params: Sequence[str] = [
            f'{param_key}="{param_val}"' for param_key, param_val in params.items()
        ]

        encoded_links.append("; ".join([link, *encoded_params]))

    response: Response = Response(
        HTTPStatus.OK, headers={"Link": ", ".join(encoded_links)}
    )

    assert dependencies.links(response) == response.links == links


def test_next_request() -> None:
    next_request: Request = Request(HTTPMethod.GET, "https://foo.bar/")

    response: Response = Response(HTTPStatus.SEE_OTHER)

    response.next_request = next_request

    assert dependencies.next_request(response) is response.next_request is next_request


def test_num_bytes_downloaded() -> None:
    text: str = "foo"

    response: Response = Response(HTTPStatus.OK, stream=ByteStream(text.encode()))

    response.read()

    assert (
        dependencies.num_bytes_downloaded(response)
        == response.num_bytes_downloaded
        == len(text)
    )


def test_reason_phrase() -> None:
    reason_phrase: str = "Foo Bar"

    response: Response = Response(
        HTTPStatus.OK, extensions={"reason_phrase": reason_phrase.encode()}
    )

    assert (
        dependencies.reason_phrase(response) == response.reason_phrase == reason_phrase
    )


def test_request() -> None:
    request: Request = Request(HTTPMethod.GET, "https://foo.bar/")

    response: Response = Response(HTTPStatus.OK, request=request)

    assert dependencies.request(response) is response.request is request


def test_response() -> None:
    response: Response = Response(HTTPStatus.OK)

    assert dependencies.response(response) is response is response


def test_status_code() -> None:
    response: Response = Response(HTTPStatus.PRECONDITION_FAILED)

    assert (
        dependencies.status_code(response)
        == response.status_code
        == HTTPStatus.PRECONDITION_FAILED
    )


def test_stream() -> None:
    stream: SyncByteStream = ByteStream(b"foo")

    response: Response = Response(HTTPStatus.OK, stream=stream)

    assert dependencies.stream(response) is response.stream is stream


def test_text() -> None:
    text: str = "foo"

    response: Response = Response(HTTPStatus.OK, text=text)

    assert dependencies.text(response) == response.text == text


def test_url() -> None:
    url: str = "https://foo.bar/"

    response: Response = Response(HTTPStatus.OK, request=Request(HTTPMethod.GET, url))

    assert dependencies.url(response) == response.url == url


def test_request_content() -> None:
    content: bytes = b"foo"

    response: Response = Response(HTTPStatus.OK, content=content)

    assert dependencies.content(response) == response.content == content


def test_request_headers() -> None:
    headers: Headers = Headers({"x-foo": "foo", "x-bar": "bar"})

    request: Request = Request(HTTPMethod.GET, "/", headers=headers)

    assert dependencies.request_headers(request) == request.headers == headers


def test_request_method() -> None:
    method: str = HTTPMethod.CONNECT

    request: Request = Request(method, "/")

    assert dependencies.request_method(request) == request.method == method


def test_request_params() -> None:
    params: QueryParams = QueryParams({"foo": "foo", "bar": "bar"})

    request: Request = Request(HTTPMethod.GET, "/", params=params)

    assert dependencies.request_params(request) == request.url.params == params


def test_request_stream() -> None:
    stream: SyncByteStream = ByteStream(b"foo")

    request: Request = Request(HTTPMethod.GET, "/", stream=stream)

    assert dependencies.request_stream(request) is request.stream is stream


def test_request_url() -> None:
    url: str = "https://foo.bar/"

    request: Request = Request(HTTPMethod.GET, url)

    assert dependencies.request_url(request) == request.url == url


def test_header() -> None:
    headers: Headers = Headers({"name": "sam"})

    assert dependencies.header("name")(headers) == "sam"
    assert dependencies.header("age")(headers) is None


def test_location() -> None:
    headers_has_location: Headers = Headers({"location": "some-location"})
    headers_no_location: Headers = Headers()

    assert dependencies.location(headers_has_location) == "some-location"
    assert dependencies.location(headers_no_location) is None


def test_server() -> None:
    headers_has_server: Headers = Headers({"server": "some-server"})
    headers_no_server: Headers = Headers()

    assert dependencies.server(headers_has_server) == "some-server"
    assert dependencies.server(headers_no_server) is None
