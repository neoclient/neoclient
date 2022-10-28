import param
import pytest

from fastclient import api
from fastclient.errors import DuplicateParameter, IncompatiblePathParameters
from fastclient.methods import get
from fastclient.operations import get_operation
from fastclient.parameter_functions import Body, Path, Query


def test_get_params_duplicate_explicit():
    with pytest.raises(DuplicateParameter):

        @get("/foo")
        def foo(a: str = Query("param"), b: str = Query("param")) -> None:
            ...


def test_get_params_duplicate_implicit():
    with pytest.raises(DuplicateParameter):

        @get("/foo")
        def foo(a: str, b: str = Query("a")) -> None:
            ...


def test_get_params_missing_path_param():
    with pytest.raises(IncompatiblePathParameters):

        @get("/foo/{path}")
        def foo() -> None:
            ...


def test_get_params_implicit():
    @get("/foo/{path}")
    def foo(path: str, query: str, body: dict) -> None:
        ...

    assert api.get_params(foo, request=get_operation(foo).specification.request) == {
        "path": param.Parameter(
            name="path",
            annotation=str,
            type=param.ParameterType.POSITIONAL_OR_KEYWORD,
            default=Path("path"),
        ),
        "query": param.Parameter(
            name="query",
            annotation=str,
            type=param.ParameterType.POSITIONAL_OR_KEYWORD,
            default=Query("query"),
        ),
        "body": param.Parameter(
            name="body",
            annotation=dict,
            type=param.ParameterType.POSITIONAL_OR_KEYWORD,
            default=Body("body"),
        ),
    }


def test_get_params_explicit():
    @get("/foo/{foo_path}")
    def foo(
        path: str = Path("foo_path"),
        query: str = Query("foo_query"),
        body: dict = Body("foo_body"),
    ) -> None:
        ...

    assert api.get_params(foo, request=get_operation(foo).specification.request) == {
        "path": param.Parameter(
            name="path",
            annotation=str,
            type=param.ParameterType.POSITIONAL_OR_KEYWORD,
            default=Path("foo_path"),
        ),
        "query": param.Parameter(
            name="query",
            annotation=str,
            type=param.ParameterType.POSITIONAL_OR_KEYWORD,
            default=Query("foo_query"),
        ),
        "body": param.Parameter(
            name="body",
            annotation=dict,
            type=param.ParameterType.POSITIONAL_OR_KEYWORD,
            default=Body("foo_body"),
        ),
    }
