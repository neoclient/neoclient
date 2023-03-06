import pytest

from neoclient.errors import DuplicateParameters
from neoclient.methods import get
from neoclient.param_functions import Query


def test_get_params_duplicate_explicit():
    with pytest.raises(DuplicateParameters):

        @get("/foo")
        def foo(a: str = Query("param"), b: str = Query("param")) -> None:
            ...


def test_get_params_duplicate_implicit():
    with pytest.raises(DuplicateParameters):

        @get("/foo")
        def foo(a: str, b: str = Query("a")) -> None:
            ...