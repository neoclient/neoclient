from typing import Any, Dict

from neoclient.validation import validate


def test_validate_all_no_defaults() -> None:
    @validate
    def func(x: int, /, y: str, *args: Any, z: int, **kwargs: Any) -> Dict[str, Any]:
        return dict(x=x, y=y, args=args, z=z, kwargs=kwargs)

    assert func(123, "abc", "cat", "dog", z=456, name="sam") == {
        "x": 123,
        "y": "abc",
        "args": ("cat", "dog"),
        "z": 456,
        "kwargs": {"name": "sam"},
    }


def test_validate_pos_or_kw_no_defaults() -> None:
    @validate
    def func(a: int, b: str) -> Dict[str, Any]:
        return dict(a=a, b=b)

    assert func(1, "foo") == {"a": 1, "b": "foo"}
    assert func(1, b="foo") == {"a": 1, "b": "foo"}
    assert func(a=1, b="foo") == {"a": 1, "b": "foo"}
    assert func(b="foo", a=1) == {"a": 1, "b": "foo"}
    assert func("123", 456) == {"a": 123, "b": "456"}  #  type: ignore


def test_validate_pos_or_kw_defaults() -> None:
    @validate
    def func(a: int = 123, b: str = "abc") -> Dict[str, Any]:
        return dict(a=a, b=b)

    assert func(456) == {"a": 456, "b": "abc"}
    assert func("456") == {"a": 456, "b": "abc"}  #  type: ignore
    assert func(a=456) == {"a": 456, "b": "abc"}
    assert func(a="456") == {"a": 456, "b": "abc"}  #  type: ignore
    assert func(b="def") == {"a": 123, "b": "def"}
    assert func(b=123) == {"a": 123, "b": "123"}  #  type: ignore
    assert func(456, "def") == {"a": 456, "b": "def"}
    assert func(a=456, b="def") == {"a": 456, "b": "def"}
    assert func(456, b="def") == {"a": 456, "b": "def"}
    assert func("456", 456) == {"a": 456, "b": "456"}  #  type: ignore
    assert func("456", b=456) == {"a": 456, "b": "456"}  #  type: ignore
    assert func(a="456", b=456) == {"a": 456, "b": "456"}  #  type: ignore
