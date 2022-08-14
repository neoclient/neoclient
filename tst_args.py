import inspect
from retrofit.api import get_arguments


def f1(a: int, b: str):
    ...


def f2(a: int = 1, b: str = "b"):
    ...


def f3(a: int, b: str = "b"):
    ...


def f4(*a: int):
    ...


def f5(*a: int, b: str = "b"):
    ...


def f6(*a: int, **b: str):
    ...


def f7():
    ...


def f8(a: int):
    ...


def f9(**a: int):
    ...


def f10(a: int = 1, **b: str):
    ...


def f11(a: int, /):
    ...


def f12(a: int, /, b: str):
    ...


def f13(a: int, /, b: str = "b"):
    ...


def f14(a: int = 1, /, b: str = "b"):
    ...


def f15(*, a: int):
    ...


def f16(a: int, *, b: str):
    ...


def f17(a: int, /, *, b: str):
    ...


def f18(a: int = 1, /, *, b: str = "b"):
    ...


def test_f1():
    assert get_arguments((1, "b"), {}, inspect.signature(f1)) == {"a": 1, "b": "b"}


def test_f2():
    assert get_arguments((), {"b": "b", "a": 1}, inspect.signature(f2)) == {
        "a": 1,
        "b": "b",
    }
