from typing import Any, Callable, Protocol, TypeVar
from typing_extensions import ParamSpec

PS = ParamSpec("PS")
RT = TypeVar("RT")


def decorate(func: Callable[..., RT], /) -> Callable[..., RT]:
    def wrap(self, *args: Any, **kwargs: Any):
        print("wrap:", self, args, kwargs)

        return func(*args, **kwargs)

    return wrap

class MyProtocol(Protocol):
    @decorate
    def my_method():
        ...