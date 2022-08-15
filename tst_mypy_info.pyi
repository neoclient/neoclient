from typing import TypeVar, overload, Literal, Callable
import enum

class Sentinel(enum.Enum):
    Missing = enum.auto()

T = TypeVar("T")

# @overload
# def Default() -> Literal[Sentinel.Missing]: ...

# @overload
# def Default(*, value: T) -> T: ...

# @overload
# def Default(*, factory: Callable[[], T]) -> T: ...