from typing import Callable, Generic, NoReturn, TypeVar, Union, Literal
from .sentinels import Missing, MissingType


T = TypeVar("T")


class Default(Generic[T]):
    _value: Union[T, MissingType]
    _factory: Union[Callable[[], T], MissingType]

    def __init__(
        self,
        value: Union[T, MissingType] = Missing,
        factory: Union[Callable[[], T], MissingType] = Missing,
    ):
        if value is not Missing and factory is not Missing:
            raise ValueError("cannot specify both `value` and `factory`")

        self._value = value
        self._factory = factory

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"

    def get(self) -> Union[T, NoReturn]:
        if self._factory is not Missing:
            return self._factory()
        elif self._value is not Missing:
            return self._value

        raise Exception("There is no default")

    def present(self) -> bool:
        return self._value is not Missing or self._factory is not Missing
