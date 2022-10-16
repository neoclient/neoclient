from fastclient import utils
import pytest


def test_get_path_params() -> None:
    assert utils.get_path_params("http://foo.com/") == set()
    assert utils.get_path_params("http://foo.com/{bar}") == {"bar"}
    assert utils.get_path_params("http://foo.com/{bar}/{bar}") == {"bar"}
    assert utils.get_path_params("http://foo.com/{bar}/{baz}") == {"bar", "baz"}

    with pytest.raises(ValueError):
        utils.get_path_params("http://foo.com/{}")

    with pytest.raises(ValueError):
        utils.get_path_params("http://foo.com/{0}")

    with pytest.raises(ValueError):
        utils.get_path_params("http://foo.com/{bar }")


def test_extract_path_params() -> None:
    assert utils.extract_path_params("http://foo.com/", "http://foo.com/") == {}
    assert utils.extract_path_params("http://foo.com/{bar}", "http://foo.com/bar") == {
        "bar": "bar"
    }
    assert utils.extract_path_params(
        "http://foo.com/{bar}/{baz}", "http://foo.com/bar/baz"
    ) == {"bar": "bar", "baz": "baz"}

    with pytest.raises(ValueError):
        utils.extract_path_params("http://foo.com/{bar}", "http://foo.com/")


def test_partially_format() -> None:
    assert utils.partially_format("foo") == "foo"
    assert utils.partially_format("foo", bar="bar") == "foo"
    assert utils.partially_format("foo/{bar}", bar="bar") == "foo/bar"
    assert utils.partially_format("foo/{bar}/{baz}", bar="bar") == "foo/bar/{baz}"
    assert utils.partially_format("foo/{bar}/{baz}", baz="baz") == "foo/{bar}/baz"
    assert (
        utils.partially_format("foo/{bar}/{baz}", bar="bar", baz="baz") == "foo/bar/baz"
    )


def test_bind_arguments() -> None:
    def foo(x: str, /, y: str = "def_y", *, z: str = "def_z"):
        ...

    assert utils.bind_arguments(foo, ("x",), {}) == {
        "x": "x",
        "y": "def_y",
        "z": "def_z",
    }
    assert utils.bind_arguments(foo, ("x", "y"), {}) == {
        "x": "x",
        "y": "y",
        "z": "def_z",
    }
    assert utils.bind_arguments(foo, ("x",), {"y": "y"}) == {
        "x": "x",
        "y": "y",
        "z": "def_z",
    }
    assert utils.bind_arguments(foo, ("x", "y"), {"z": "z"}) == {
        "x": "x",
        "y": "y",
        "z": "z",
    }
    assert utils.bind_arguments(foo, ("x",), {"y": "y", "z": "z"}) == {
        "x": "x",
        "y": "y",
        "z": "z",
    }
