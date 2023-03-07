from typing import Mapping, Union

import pytest
from httpx import QueryParams
from pydantic.fields import FieldInfo, Undefined

from neoclient import utils


def test_parse_format_string() -> None:
    assert utils.parse_format_string("http://foo.com/") == set()
    assert utils.parse_format_string("http://foo.com/{bar}") == {"bar"}
    assert utils.parse_format_string("http://foo.com/{bar!r}") == {"bar"}
    assert utils.parse_format_string("http://foo.com/{bar}/{bar}") == {"bar"}
    assert utils.parse_format_string("http://foo.com/{bar}/{baz}") == {"bar", "baz"}
    assert utils.parse_format_string("http://foo.com/{bar}/{{baz}}") == {"bar"}

    with pytest.raises(ValueError):
        utils.parse_format_string("http://foo.com/{}")

    with pytest.raises(ValueError):
        utils.parse_format_string("http://foo.com/{0}")

    with pytest.raises(ValueError):
        utils.parse_format_string("http://foo.com/{bar }")


def test_bind_arguments() -> None:
    def foo(
        param_1: str,
        /,
        param_2: str = "param_2_default",
        *,
        param_3: str = "param_3_default",
    ):
        ...

    assert utils.bind_arguments(foo, ("param_1",), {}) == {
        "param_1": "param_1",
        "param_2": "param_2_default",
        "param_3": "param_3_default",
    }
    assert utils.bind_arguments(foo, ("param_1", "param_2"), {}) == {
        "param_1": "param_1",
        "param_2": "param_2",
        "param_3": "param_3_default",
    }
    assert utils.bind_arguments(foo, ("param_1",), {"param_2": "param_2"}) == {
        "param_1": "param_1",
        "param_2": "param_2",
        "param_3": "param_3_default",
    }
    assert utils.bind_arguments(
        foo, ("param_1", "param_2"), {"param_3": "param_3"}
    ) == {
        "param_1": "param_1",
        "param_2": "param_2",
        "param_3": "param_3",
    }
    assert utils.bind_arguments(
        foo, ("param_1",), {"param_2": "param_2", "param_3": "param_3"}
    ) == {
        "param_1": "param_1",
        "param_2": "param_2",
        "param_3": "param_3",
    }


def test_is_primitive() -> None:
    class Foo:
        pass

    assert utils.is_primitive("abc")
    assert utils.is_primitive(123)
    assert utils.is_primitive(123.456)
    assert utils.is_primitive(True)
    assert utils.is_primitive(False)
    assert utils.is_primitive(None)
    assert not utils.is_primitive(Foo)
    assert not utils.is_primitive(Foo())


def test_unpack_arguments() -> None:
    def positional_only(arg: str, /):
        ...

    def positional_or_keyword(arg: str):
        ...

    def keyword_only(*, arg: str):
        ...

    def var_positional(*args: str):
        ...

    def var_keyword(**kwargs: str):
        ...

    def kitchen_sink(
        param_positional_only: str,
        /,
        param_positional_or_keyword: str,
        *param_var_positional: str,
        param_keyword_only: str,
        **param_var_keyword: str,
    ):
        ...

    assert utils.unpack_arguments(positional_only, {"arg": "foo"}) == (("foo",), {})
    assert utils.unpack_arguments(positional_or_keyword, {"arg": "foo"}) == (
        (),
        {"arg": "foo"},
    )
    assert utils.unpack_arguments(keyword_only, {"arg": "foo"}) == ((), {"arg": "foo"})
    assert utils.unpack_arguments(var_positional, {"args": ("foo", "bar", "baz")}) == (
        ("foo", "bar", "baz"),
        {},
    )
    assert utils.unpack_arguments(
        var_keyword, {"kwargs": {"name": "sam", "age": 43}}
    ) == ((), {"name": "sam", "age": 43})
    assert utils.unpack_arguments(
        kitchen_sink,
        {
            "param_positional_only": "param_positional_only",
            "param_positional_or_keyword": "param_positional_or_keyword",
            "param_var_positional": ("arg1", "arg2"),
            "param_keyword_only": "param_keyword_only",
            "param_var_keyword": {"key1": "val1", "key2": "val2"},
        },
    ) == (
        ("param_positional_only", "arg1", "arg2"),
        {
            "param_positional_or_keyword": "param_positional_or_keyword",
            "param_keyword_only": "param_keyword_only",
            "key1": "val1",
            "key2": "val2",
        },
    )

    with pytest.raises(ValueError):
        utils.unpack_arguments(positional_only, {})


def test_get_default() -> None:
    assert utils.get_default(FieldInfo(default_factory=dict)) == {}
    assert utils.get_default(FieldInfo(default="abc")) == "abc"
    assert utils.get_default(FieldInfo()) == Undefined


def test_has_default() -> None:
    assert utils.has_default(FieldInfo(default_factory=dict))
    assert utils.has_default(FieldInfo(default="abc"))
    assert not utils.has_default(FieldInfo())


def test_parse_obj_as() -> None:
    assert utils.parse_obj_as(str, "123") == "123"
    assert utils.parse_obj_as(str, 123) == "123"
    assert utils.parse_obj_as(Union[str, int], "abc") == "abc"  # type: ignore
    assert utils.parse_obj_as(
        Mapping[str, str], QueryParams({"name": "sam", "age": "43"})  # type: ignore
    ) == QueryParams({"name": "sam", "age": "43"})
