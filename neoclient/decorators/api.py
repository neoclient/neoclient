from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Optional, Sequence, Tuple, Type, TypeVar

from httpx import Headers
from neoclient import converters
from neoclient.operation import Operation, get_operation
from neoclient.services import Service
from neoclient.specification import ClientSpecification
from neoclient.types import HeaderTypes
from neoclient.typing import Consumer
from neoclient import typing

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
        raise DecorationError("Decorating operation not supported")

    def decorate_client(self, client: ClientSpecification, /) -> None:
        raise DecorationError("Decorating client not supported")


# @dataclass
# class ConsumerDecorator(Decorator):
#     consume_operation: Optional[Consumer[Operation]] = None
#     consume_client: Optional[Consumer[ClientSpecification]] = None

#     def decorate_operation(self, operation: Operation, /) -> None:
#         if self.consume_operation is None:
#             super().decorate_operation(operation)

#         self.consume_operation(operation)

#     def decorate_client(self, client: ClientSpecification, /) -> None:
#         if self.consume_client is None:
#             super().decorate_client(client)

#         self.consume_client(client)


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


def operation_decorator(consumer: Consumer[Operation], /):
    return OperationDecorator(consumer)


def client_decorator(consumer: Consumer[ClientSpecification], /):
    return ClientDecorator(consumer)


# def headers_decorator(consumer: Consumer[Headers], /):
#     def consume_operation(operation: Operation, /) -> None:
#         return consumer(operation.pre_request.headers)

#     def consume_client(client: ClientSpecification, /) -> None:
#         return consumer(client.options.headers)

#     return ConsumerDecorator(
#         consume_operation=consume_operation, consume_client=consume_client
#     )


# def header_decorator(key: str, value: HeaderTypes, /):
#     values: Sequence[str] = converters.convert_header(value)

#     def consume_headers(headers: Headers, /) -> None:
#         # If there's only one value, set the header and overwrite any existing
#         # entries for this key
#         if len(values) == 1:
#             headers[key] = values[0]
#         # Otherwise, update the headers and maintain any existing entries for this
#         # key
#         else:
#             values: Sequence[Tuple[str, str]] = [(key, value) for value in values]

#             headers.update(values)

#     return headers_decorator(consume_headers)


@dataclass
class HeadersDecorator(Decorator):
    consumer: Consumer[Headers]

    def decorate_operation(self, operation: Operation, /) -> None:
        return self.consumer(operation.pre_request.headers)

    def decorate_client(self, client: ClientSpecification, /) -> None:
        return self.consumer(client.options.headers)


def headers_decorator(consumer: Consumer[Headers], /):
    return HeadersDecorator(consumer)


# class HeadersDecorator(Decorator, ABC):
#     @abstractmethod
#     def decorate_headers(self, headers: Headers, /) -> None:
#         raise NotImplementedError

#     def decorate_operation(self, operation: Operation, /) -> None:
#         return self.decorate_headers(operation.pre_request.headers)

#     def decorate_client(self, client: ClientSpecification, /) -> None:
#         return self.decorate_headers(client.options.headers)


# @dataclass(init=False)
# class HeaderConsumer(Consumer[Headers]):
#     key: str
#     values: Sequence[str]

#     def __init__(self, key: str, value: HeaderTypes) -> None:
#         self.key = key
#         self.values = converters.convert_header(value)

#     def __call__(self, headers: Headers, /) -> None:
#         # If there's only one value, set the header and overwrite any existing
#         # entries for this key
#         if len(self.values) == 1:
#             headers[self.key] = self.values[0]
#         # Otherwise, update the headers and maintain any existing entries for this
#         # key
#         else:
#             values: Sequence[Tuple[str, str]] = [
#                 (self.key, value) for value in self.values
#             ]

#             headers.update(values)


# def header_decorator(key: str, value: HeaderTypes, /):
#     return HeaderDecorator(key, value)
