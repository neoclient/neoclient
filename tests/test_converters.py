from httpx import Cookies, Headers, QueryParams, Timeout

from neoclient import converters


def test_convert_query_param() -> None:
    assert converters.convert_query_param("abc") == ["abc"]
    assert converters.convert_query_param(123) == ["123"]
    assert converters.convert_query_param(1.0) == ["1.0"]
    assert converters.convert_query_param(True) == ["true"]
    assert converters.convert_query_param(None) == [""]

    assert converters.convert_query_param(("abc", "def")) == ["abc", "def"]
    assert converters.convert_query_param((123, 456)) == ["123", "456"]
    assert converters.convert_query_param((1.0, 2.0)) == ["1.0", "2.0"]
    assert converters.convert_query_param((True, False)) == ["true", "false"]
    assert converters.convert_query_param((None, None)) == ["", ""]


def test_convert_header() -> None:
    assert converters.convert_header("abc") == ["abc"]
    assert converters.convert_header(123) == ["123"]
    assert converters.convert_header(1.0) == ["1.0"]
    assert converters.convert_header(True) == ["true"]
    assert converters.convert_header(None) == [""]

    assert converters.convert_header(("abc", "def")) == ["abc", "def"]
    assert converters.convert_header((123, 456)) == ["123", "456"]
    assert converters.convert_header((1.0, 2.0)) == ["1.0", "2.0"]
    assert converters.convert_header((True, False)) == ["true", "false"]
    assert converters.convert_header((None, None)) == ["", ""]


def test_convert_cookie() -> None:
    assert converters.convert_cookie("abc") == "abc"
    assert converters.convert_cookie(123) == "123"
    assert converters.convert_cookie(1.0) == "1.0"
    assert converters.convert_cookie(True) == "true"
    assert converters.convert_cookie(None) == ""


def test_convert_path() -> None:
    assert converters.convert_path_param("abc") == "abc"
    assert converters.convert_path_param(123) == "123"
    assert converters.convert_path_param(1.0) == "1.0"
    assert converters.convert_path_param(True) == "true"
    assert converters.convert_path_param(None) == ""

    assert converters.convert_path_param(("abc", "def")) == "abc/def"
    assert converters.convert_path_param((123, 456)) == "123/456"
    assert converters.convert_path_param((1.0, 2.5)) == "1.0/2.5"
    assert converters.convert_path_param((True, False)) == "true/false"
    assert converters.convert_path_param(("abc", None, "def")) == "abc/def"


def test_convert_query_params() -> None:
    assert converters.convert_query_params(
        QueryParams({"name": "sam", "age": "43"})
    ) == QueryParams({"name": "sam", "age": "43"})
    assert converters.convert_query_params({"name": "sam", "age": "43"}) == QueryParams(
        {"name": "sam", "age": "43"}
    )
    assert converters.convert_query_params(
        (("name", "sam"), ("age", "43"))
    ) == QueryParams({"name": "sam", "age": "43"})
    assert converters.convert_query_params(("name", "age")) == QueryParams(
        {"name": "", "age": ""}
    )
    assert converters.convert_query_params("name=sam&age=43") == QueryParams(
        {"name": "sam", "age": "43"}
    )


def test_convert_headers() -> None:
    assert converters.convert_headers(Headers({"name": "sam", "age": "43"})) == Headers(
        {"name": "sam", "age": "43"}
    )
    assert converters.convert_headers({"name": "sam", "age": "43"}) == Headers(
        {"name": "sam", "age": "43"}
    )
    assert converters.convert_headers((("name", "sam"), ("age", "43"))) == Headers(
        {"name": "sam", "age": "43"}
    )


def test_convert_cookies() -> None:
    assert converters.convert_cookies(Cookies({"name": "sam", "age": "43"})) == Cookies(
        {"name": "sam", "age": "43"}
    )
    assert converters.convert_cookies({"name": "sam", "age": "43"}) == Cookies(
        {"name": "sam", "age": "43"}
    )
    assert converters.convert_cookies((("name", "sam"), ("age", "43"))) == Cookies(
        {"name": "sam", "age": "43"}
    )


def test_convert_path_params() -> None:
    assert converters.convert_path_params({"name": "sam", "age": "43"}) == {
        "name": "sam",
        "age": "43",
    }
    assert converters.convert_path_params({"names": ("sam", "bob")}) == {
        "names": "sam/bob",
    }


def test_convert_timeout() -> None:
    assert converters.convert_timeout(1.25) == Timeout(1.25)
    assert converters.convert_timeout(None) == Timeout(None)
    assert converters.convert_timeout(Timeout(1.5)) == Timeout(1.5)
