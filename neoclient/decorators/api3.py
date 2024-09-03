from abc import ABC, abstractmethod
from typing import Any, Callable, Type, TypeVar

from httpx import Headers
from neoclient.operation import Operation, get_operation
from neoclient.services import Service
from neoclient.specification import ClientSpecification

CS = TypeVar("CS", Callable[..., Any], Type[Service])


class DecorationError(Exception):
    pass


class Decorator:
    def __call__(self, target: CS, /) -> CS:
        if isinstance(target, type):
            if not issubclass(target, Service):
                raise DecorationError(f"Target class is not a subclass of {Service}")

            specification: ClientSpecification = target._spec

            self.decorate_client(specification)
        elif callable(target):
            operation: Operation = get_operation(target)

            self.decorate_operation(operation)
        else:
            raise DecorationError(f"Target of unsupported type {type(target)}")

        return target

    def decorate_operation(self, operation: Operation, /) -> None:
        raise Exception("Decorating operation not supported")

    def decorate_client(self, client: ClientSpecification, /) -> None:
        raise Exception("Decorating client not supported")


class HeadersDecorator(Decorator, ABC):
    @abstractmethod
    def decorate_headers(self, headers: Headers, /) -> None:
        raise NotImplementedError

    def decorate_operation(self, operation: Operation, /) -> None:
        return self.decorate_headers(operation.pre_request.headers)

    def decorate_client(self, client: ClientSpecification, /) -> None:
        return self.decorate_headers(client.options.headers)
