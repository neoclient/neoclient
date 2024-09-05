from dataclasses import dataclass
from typing import Any, Callable, Type, TypeVar, Union

from httpx import Cookies, Headers
from neoclient.middlewares import Middleware
from neoclient.operation import Operation, get_operation
from neoclient.services import Service
from neoclient.specification import ClientSpecification
from neoclient.typing import Consumer

CS = TypeVar("CS", Callable[..., Any], Type[Service])

DecoratorTarget = Union[Operation, ClientSpecification]

# DT = TypeVar("DT", DecoratorTarget)


class DecorationError(Exception):
    pass


# def decorator(consumer: Consumer[DecoratorTarget], /):
#     def decorate(target: CS, /) -> CS:
#         if isinstance(target, type):
#             if not issubclass(target, Service):
#                 raise DecorationError(f"Target class is not a subclass of {Service}")

#             specification: ClientSpecification = target._spec

#             consumer(specification)
#         elif callable(target):
#             operation: Operation = get_operation(target)

#             consumer(operation)
#         else:
#             raise DecorationError(f"Target of unsupported type {type(target)}")

#         return target

#     return decorate


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
        raise DecorationError("Decorating operation not supported")

    def decorate_client(self, client: ClientSpecification, /) -> None:
        raise DecorationError("Decorating client not supported")


@dataclass
class CommonDecorator(Decorator):
    consumer: Consumer[DecoratorTarget]

    def decorate_operation(self, operation: Operation, /) -> None:
        return self.consumer(operation)

    def decorate_client(self, client: ClientSpecification, /) -> None:
        return self.consumer(client)


@dataclass
class OperationDecorator(Decorator):
    consumer: Consumer[Operation]

    def decorate_operation(self, operation: Operation, /) -> None:
        self.consume_operation(operation)


@dataclass
class ClientDecorator(Decorator):
    consumer: Consumer[Operation]

    def decorate_operation(self, operation: Operation, /) -> None:
        self.consume_operation(operation)


@dataclass
class HeadersDecorator(Decorator):
    consumer: Consumer[Headers]

    def decorate_operation(self, operation: Operation, /) -> None:
        return self.consumer(operation.pre_request.headers)

    def decorate_client(self, client: ClientSpecification, /) -> None:
        return self.consumer(client.options.headers)


@dataclass
class CookiesDecorator(Decorator):
    consumer: Consumer[Cookies]

    def decorate_operation(self, operation: Operation, /) -> None:
        return self.consumer(operation.pre_request.cookies)

    def decorate_client(self, client: ClientSpecification, /) -> None:
        return self.consumer(client.options.cookies)


@dataclass
class MiddlewareDecorator(Decorator):
    consumer: Consumer[Middleware]

    def decorate_operation(self, operation: Operation, /) -> None:
        return self.consumer(operation.middleware)

    def decorate_client(self, client: ClientSpecification, /) -> None:
        return self.consumer(client.middleware)


def common_decorator(consumer: Consumer[DecoratorTarget], /):
    return CommonDecorator(consumer)


def operation_decorator(consumer: Consumer[Operation], /):
    return OperationDecorator(consumer)


def client_decorator(consumer: Consumer[ClientSpecification], /):
    return ClientDecorator(consumer)


def headers_decorator(consumer: Consumer[Headers], /):
    return HeadersDecorator(consumer)


def middleware_decorator(consumer: Consumer[Middleware], /):
    return MiddlewareDecorator(consumer)
