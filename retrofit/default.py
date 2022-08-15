from typing import Callable, Generic, Literal, NoReturn, TypeVar, Union, Literal
import enum


T = TypeVar("T")


class Sentinel(enum.Enum):
    Missing = enum.auto()


class Default(Generic[T]):
    _value: Union[T, Literal[Sentinel.Missing]]
    _factory: Union[Callable[[], T], Literal[Sentinel.Missing]]

    def __init__(
        self,
        value: Union[T, Literal[Sentinel.Missing]] = Sentinel.Missing,
        factory: Union[Callable[[], T], Literal[Sentinel.Missing]] = Sentinel.Missing,
    ):
        if value is not Sentinel.Missing and factory is not Sentinel.Missing:
            raise ValueError("cannot specify both `value` and `factory`")

        self._value = value
        self._factory = factory

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"

    def get(self) -> Union[T, NoReturn]:
        if self._factory is not Sentinel.Missing:
            return self._factory()
        elif self._value is not Sentinel.Missing:
            return self._value

        raise Exception("There is no default")

    def present(self) -> bool:
        return (
            self._value is not Sentinel.Missing or self._factory is not Sentinel.Missing
        )
