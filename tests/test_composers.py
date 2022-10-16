import pytest
from fastclient import (
    Query,
    Header,
    Cookie,
    Path,
    QueryParams,
    Headers,
    Cookies,
    PathParams,
)
from fastclient import composers
from param.errors import ResolutionError
from pydantic.fields import Undefined
import httpx

from fastclient.models import RequestOptions


def test_compose_query_param_default_no_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_query_param(
        request=request,
        param=Query(alias="foo", default="bar"),
        value=Undefined,
    )

    assert request == RequestOptions(
        "GET", "/", params=httpx.QueryParams({"foo": "bar"})
    )


def test_compose_query_param_default_factory_no_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_query_param(
        request=request,
        param=Query(alias="foo", default_factory=lambda: "bar"),
        value=Undefined,
    )

    assert request == RequestOptions(
        "GET", "/", params=httpx.QueryParams({"foo": "bar"})
    )


def test_compose_query_param_default_has_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_query_param(
        request=request,
        param=Query(alias="foo", default="bar"),
        value="baz",
    )

    assert request == RequestOptions(
        "GET", "/", params=httpx.QueryParams({"foo": "baz"})
    )


def test_compose_query_param_default_factory_has_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_query_param(
        request=request,
        param=Query(alias="foo", default_factory=lambda: "bar"),
        value="baz",
    )

    assert request == RequestOptions(
        "GET", "/", params=httpx.QueryParams({"foo": "baz"})
    )


def test_compose_query_param_no_default_no_arg() -> None:
    with pytest.raises(ResolutionError):
        composers.compose_query_param(
            request=RequestOptions("GET", "/"),
            param=Query(alias="foo"),
            value=Undefined,
        )


def test_compose_query_param_no_alias() -> None:
    with pytest.raises(ResolutionError):
        composers.compose_query_param(
            request=RequestOptions("GET", "/"),
            param=Query(default="bar"),
            value="baz",
        )


def test_compose_header_default_no_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_header(
        request=request,
        param=Header(alias="foo", default="bar"),
        value=Undefined,
    )

    assert request == RequestOptions("GET", "/", headers=httpx.Headers({"foo": "bar"}))


def test_compose_header_default_factory_no_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_header(
        request=request,
        param=Header(alias="foo", default_factory=lambda: "bar"),
        value=Undefined,
    )

    assert request == RequestOptions("GET", "/", headers=httpx.Headers({"foo": "bar"}))


def test_compose_header_default_has_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_header(
        request=request,
        param=Header(alias="foo", default="bar"),
        value="baz",
    )

    assert request == RequestOptions("GET", "/", headers=httpx.Headers({"foo": "baz"}))


def test_compose_header_default_factory_has_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_header(
        request=request,
        param=Header(alias="foo", default_factory=lambda: "bar"),
        value="baz",
    )

    assert request == RequestOptions("GET", "/", headers=httpx.Headers({"foo": "baz"}))


def test_compose_header_no_default_no_arg() -> None:
    with pytest.raises(ResolutionError):
        composers.compose_header(
            request=RequestOptions("GET", "/"),
            param=Header(alias="foo"),
            value=Undefined,
        )


def test_compose_header_no_alias() -> None:
    with pytest.raises(ResolutionError):
        composers.compose_header(
            request=RequestOptions("GET", "/"),
            param=Header(default="bar"),
            value="baz",
        )


def test_compose_cookie_default_no_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_cookie(
        request=request,
        param=Cookie(alias="foo", default="bar"),
        value=Undefined,
    )

    assert request == RequestOptions("GET", "/", cookies=httpx.Cookies({"foo": "bar"}))


def test_compose_cookie_default_factory_no_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_cookie(
        request=request,
        param=Cookie(alias="foo", default_factory=lambda: "bar"),
        value=Undefined,
    )

    assert request == RequestOptions("GET", "/", cookies=httpx.Cookies({"foo": "bar"}))


def test_compose_cookie_default_has_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_cookie(
        request=request,
        param=Cookie(alias="foo", default="bar"),
        value="baz",
    )

    assert request == RequestOptions("GET", "/", cookies=httpx.Cookies({"foo": "baz"}))


def test_compose_cookie_default_factory_has_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_cookie(
        request=request,
        param=Cookie(alias="foo", default_factory=lambda: "bar"),
        value="baz",
    )

    assert request == RequestOptions("GET", "/", cookies=httpx.Cookies({"foo": "baz"}))


def test_compose_cookie_no_default_no_arg() -> None:
    with pytest.raises(ResolutionError):
        composers.compose_cookie(
            request=RequestOptions("GET", "/"),
            param=Cookie(alias="foo"),
            value=Undefined,
        )


def test_compose_cookie_no_alias() -> None:
    with pytest.raises(ResolutionError):
        composers.compose_cookie(
            request=RequestOptions("GET", "/"),
            param=Cookie(default="bar"),
            value="baz",
        )


def test_compose_path_param_default_no_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/{foo}")

    composers.compose_path_param(
        request=request,
        param=Path(alias="foo", default="bar"),
        value=Undefined,
    )

    assert request == RequestOptions("GET", "/bar")


def test_compose_path_param_default_factory_no_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/{foo}")

    composers.compose_path_param(
        request=request,
        param=Path(alias="foo", default_factory=lambda: "bar"),
        value=Undefined,
    )

    assert request == RequestOptions("GET", "/bar")


def test_compose_path_param_default_has_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/{foo}")

    composers.compose_path_param(
        request=request,
        param=Path(alias="foo", default="bar"),
        value="baz",
    )

    assert request == RequestOptions("GET", "/baz")


def test_compose_path_param_default_factory_has_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/{foo}")

    composers.compose_path_param(
        request=request,
        param=Path(alias="foo", default_factory=lambda: "bar"),
        value="baz",
    )

    assert request == RequestOptions("GET", "/baz")


def test_compose_path_param_no_default_no_arg() -> None:
    with pytest.raises(ResolutionError):
        composers.compose_path_param(
            request=RequestOptions("GET", "/"),
            param=Path(alias="foo"),
            value=Undefined,
        )


def test_compose_path_param_no_alias() -> None:
    with pytest.raises(ResolutionError):
        composers.compose_path_param(
            request=RequestOptions("GET", "/{foo}"),
            param=Path(default="bar"),
            value="baz",
        )


def test_compose_query_params_default_no_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_query_params(
        request=request,
        param=QueryParams(default={"foo": "bar"}),
        value=Undefined,
    )

    assert request == RequestOptions(
        "GET", "/", params=httpx.QueryParams({"foo": "bar"})
    )


def test_compose_query_params_default_factory_no_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_query_params(
        request=request,
        param=QueryParams(default_factory=lambda: {"foo": "bar"}),
        value=Undefined,
    )

    assert request == RequestOptions(
        "GET", "/", params=httpx.QueryParams({"foo": "bar"})
    )


def test_compose_query_params_default_has_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_query_params(
        request=request,
        param=QueryParams(default={"foo": "bar"}),
        value={"foo": "baz"},
    )

    assert request == RequestOptions(
        "GET", "/", params=httpx.QueryParams({"foo": "baz"})
    )


def test_compose_query_params_default_factory_has_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_query_params(
        request=request,
        param=QueryParams(default_factory=lambda: {"foo": "bar"}),
        value={"foo": "baz"},
    )

    assert request == RequestOptions(
        "GET", "/", params=httpx.QueryParams({"foo": "baz"})
    )


def test_compose_query_params_no_default_no_arg() -> None:
    with pytest.raises(ResolutionError):
        composers.compose_query_params(
            request=RequestOptions("GET", "/"),
            param=QueryParams(),
            value=Undefined,
        )


def test_compose_headers_default_no_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_headers(
        request=request,
        param=Headers(default={"foo": "bar"}),
        value=Undefined,
    )

    assert request == RequestOptions("GET", "/", headers=httpx.Headers({"foo": "bar"}))


def test_compose_headers_default_factory_no_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_headers(
        request=request,
        param=Headers(default_factory=lambda: {"foo": "bar"}),
        value=Undefined,
    )

    assert request == RequestOptions("GET", "/", headers=httpx.Headers({"foo": "bar"}))


def test_compose_headers_default_has_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_headers(
        request=request,
        param=Headers(default={"foo": "bar"}),
        value={"foo": "baz"},
    )

    assert request == RequestOptions("GET", "/", headers=httpx.Headers({"foo": "baz"}))


def test_compose_headers_default_factory_has_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_headers(
        request=request,
        param=Headers(default_factory=lambda: {"foo": "bar"}),
        value={"foo": "baz"},
    )

    assert request == RequestOptions("GET", "/", headers=httpx.Headers({"foo": "baz"}))


def test_compose_headers_no_default_no_arg() -> None:
    with pytest.raises(ResolutionError):
        composers.compose_headers(
            request=RequestOptions("GET", "/"),
            param=Headers(),
            value=Undefined,
        )


def test_compose_cookies_default_no_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_cookies(
        request=request,
        param=Cookies(default={"foo": "bar"}),
        value=Undefined,
    )

    assert request == RequestOptions("GET", "/", cookies=httpx.Cookies({"foo": "bar"}))


def test_compose_cookies_default_factory_no_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_cookies(
        request=request,
        param=Cookies(default_factory=lambda: {"foo": "bar"}),
        value=Undefined,
    )

    assert request == RequestOptions("GET", "/", cookies=httpx.Cookies({"foo": "bar"}))


def test_compose_cookies_default_has_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_cookies(
        request=request,
        param=Cookies(default={"foo": "bar"}),
        value={"foo": "baz"},
    )

    assert request == RequestOptions("GET", "/", cookies=httpx.Cookies({"foo": "baz"}))


def test_compose_cookies_default_factory_has_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_cookies(
        request=request,
        param=Cookies(default_factory=lambda: {"foo": "bar"}),
        value={"foo": "baz"},
    )

    assert request == RequestOptions("GET", "/", cookies=httpx.Cookies({"foo": "baz"}))


def test_compose_cookies_no_default_no_arg() -> None:
    with pytest.raises(ResolutionError):
        composers.compose_cookies(
            request=RequestOptions("GET", "/"),
            param=Cookies(),
            value=Undefined,
        )


def test_compose_path_params_default_no_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/{foo}")

    composers.compose_path_params(
        request=request,
        param=PathParams(default={"foo": "bar"}),
        value=Undefined,
    )

    assert request == RequestOptions("GET", "/bar")


def test_compose_path_params_default_factory_no_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/{foo}")

    composers.compose_path_params(
        request=request,
        param=PathParams(default_factory=lambda: {"foo": "bar"}),
        value=Undefined,
    )

    assert request == RequestOptions("GET", "/bar")


def test_compose_path_params_default_has_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/{foo}")

    composers.compose_path_params(
        request=request,
        param=PathParams(default={"foo": "bar"}),
        value={"foo": "baz"},
    )

    assert request == RequestOptions("GET", "/baz")


def test_compose_path_params_default_factory_has_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/{foo}")

    composers.compose_path_params(
        request=request,
        param=PathParams(default_factory=lambda: {"foo": "bar"}),
        value={"foo": "baz"},
    )

    assert request == RequestOptions("GET", "/baz")


def test_compose_path_params_no_default_no_arg() -> None:
    with pytest.raises(ResolutionError):
        composers.compose_path_params(
            request=RequestOptions("GET", "/{foo}"),
            param=PathParams(),
            value=Undefined,
        )
