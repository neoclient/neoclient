from typing import Generic, TypeVar
from typing_extensions import Annotated

# T = TypeVar("T")


# class SomeAnnotation:
#     __slots__ = ('type', )

#     def __init__(self, type):
#         self.type = type

#     def __repr__(self):
#         if isinstance(self.type, type):
#             type_name = self.type.__name__
#         else:
#             # typing objects, e.g. List[int]
#             type_name = repr(self.type)

#         return f'SomeAnnotation[{type_name}]'

#     def __class_getitem__(cls, type):
#         return SomeAnnotation(type)

# class SomeOtherAnnotation(Generic[T]): pass


# def foo(bar: SomeAnnotation[int]) -> int:
#     return bar

# print(foo(123))

# def foo(bar: SomeOtherAnnotation[int]) -> int:
#     return bar

# print(foo(123))

Path = Annotated[int, "path"]


def foo(x: Path = 123) -> int:
    return x
