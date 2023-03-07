from typing import Any, Dict

from neoclient.validation import validate


def test_validate_all_no_defaults() -> None:
    @validate
    def func(
        param_1: int, /, param_2: str, *args: Any, param_3: int, **kwargs: Any
    ) -> Dict[str, Any]:
        return {
            "param_1": param_1,
            "param_2": param_2,
            "args": args,
            "param_3": param_3,
            "kwargs": kwargs,
        }

    assert func(123, "abc", "cat", "dog", param_3=456, name="sam") == {
        "param_1": 123,
        "param_2": "abc",
        "args": ("cat", "dog"),
        "param_3": 456,
        "kwargs": {"name": "sam"},
    }


def test_validate_pos_or_kw_no_defaults() -> None:
    @validate
    def func(param_1: int, param_2: str) -> Dict[str, Any]:
        return {"param_1": param_1, "param_2": param_2}

    assert func(1, "foo") == {"param_1": 1, "param_2": "foo"}
    assert func(1, param_2="foo") == {"param_1": 1, "param_2": "foo"}
    assert func(param_1=1, param_2="foo") == {"param_1": 1, "param_2": "foo"}
    assert func(param_2="foo", param_1=1) == {"param_1": 1, "param_2": "foo"}
    assert func("123", 456) == {"param_1": 123, "param_2": "456"}  #  type: ignore


def test_validate_pos_or_kw_defaults() -> None:
    @validate
    def func(param_1: int = 123, param_2: str = "abc") -> Dict[str, Any]:
        return {"param_1": param_1, "param_2": param_2}

    assert func(456) == {"param_1": 456, "param_2": "abc"}
    assert func("456") == {"param_1": 456, "param_2": "abc"}  #  type: ignore
    assert func(param_1=456) == {"param_1": 456, "param_2": "abc"}
    assert func(param_1="456") == {"param_1": 456, "param_2": "abc"}  #  type: ignore
    assert func(param_2="def") == {"param_1": 123, "param_2": "def"}
    assert func(param_2=123) == {"param_1": 123, "param_2": "123"}  #  type: ignore
    assert func(456, "def") == {"param_1": 456, "param_2": "def"}
    assert func(param_1=456, param_2="def") == {"param_1": 456, "param_2": "def"}
    assert func(456, param_2="def") == {"param_1": 456, "param_2": "def"}
    assert func("456", 456) == {"param_1": 456, "param_2": "456"}  #  type: ignore
    assert func("456", param_2=456) == {  #  type: ignore
        "param_1": 456,
        "param_2": "456",
    }
    assert func(param_1="456", param_2=456) == {  #  type: ignore
        "param_1": 456,
        "param_2": "456",
    }
