from ..operation import Operation
from ..specification import ClientSpecification
from ..typing import Dependency
from .api import DecoratorTarget, common_decorator

__all__ = ("response",)

# TODO: Type return values


def response(dependency: Dependency, /):
    @common_decorator
    def decorate(target: DecoratorTarget, /) -> None:
        if isinstance(target, ClientSpecification):
            target.default_response = dependency
        elif isinstance(target, Operation):
            target.response = dependency
        else:
            raise TypeError

    return decorate
