from typing import Callable


def make_staticmethod(func: Callable, /) -> staticmethod:
    return staticmethod(func)
    
class MyClass:
    @make_staticmethod
    def my_method():
        ...

# class MyClass:
#     @staticmethod
#     def my_method():
#         ...
