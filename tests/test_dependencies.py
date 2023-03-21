from http import HTTPStatus

from httpx import Cookies, Response


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


def test_encoding() -> None:
    encoding: str = "foo"

    response: Response = Response(HTTPStatus.OK, default_encoding=encoding)

    assert response.encoding == encoding


def test_cookies() -> None:
    cookies: Cookies = Cookies({"x-foo": "bar"})

    # TODO!
    assert 1 == 2
