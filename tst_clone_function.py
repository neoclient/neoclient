from typing import Callable, TypeVar
from typing_extensions import ParamSpec

Params = ParamSpec("Params")
Return = TypeVar("Return")


def decorate(func: Callable[Params, Return], /) -> Callable[Params, Return]:
    def wrap(*args: Params.args, **kwargs: Params.kwargs) -> Return:
        return func(*args, **kwargs)

    return wrap


@decorate
def foo(a: int, b: str = "b") -> bool:
    return a == 123 and b == "abc"


# print(foo(1, "b"))
# print(foo(123, "abc"))

foo(1)
