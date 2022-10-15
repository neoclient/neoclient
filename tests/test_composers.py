from fastclient import Query
from fastclient import composers
from pydantic.fields import Undefined
from httpx import QueryParams

from fastclient.models import ComposerContext, RequestOptions


def test_compose_query_param_default_no_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_query_param(
        field=Query(alias="foo", default="bar"),
        value=Undefined,
        context=ComposerContext(request=request),
    )

    assert request == RequestOptions("GET", "/", params=QueryParams({"foo": "bar"}))


def test_compose_query_param_default_factory_no_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_query_param(
        field=Query(alias="foo", default_factory=lambda: "bar"),
        value=Undefined,
        context=ComposerContext(
            request=request,
            parameters={},
        ),
    )

    assert request == RequestOptions("GET", "/", params=QueryParams({"foo": "bar"}))


def test_compose_query_param_default_has_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_query_param(
        field=Query(alias="foo", default="bar"),
        value="baz",
        context=ComposerContext(request=request),
    )

    assert request == RequestOptions("GET", "/", params=QueryParams({"foo": "baz"}))


def test_compose_query_param_default_factory_has_arg() -> None:
    request: RequestOptions = RequestOptions("GET", "/")

    composers.compose_query_param(
        field=Query(alias="foo", default_factory=lambda: "bar"),
        value="baz",
        context=ComposerContext(
            request=request,
            parameters={},
        ),
    )

    assert request == RequestOptions("GET", "/", params=QueryParams({"foo": "baz"}))
