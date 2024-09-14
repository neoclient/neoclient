from dataclasses import dataclass
from typing import Any, Callable, MutableSequence, Type, TypeVar, Union

from httpx import Cookies, Headers, QueryParams
from neoclient.middlewares import Middleware
from neoclient.models import ClientOptions, RequestOptions
from neoclient.operation import Operation, get_operation
from neoclient.services import Service
from neoclient.specification import ClientSpecification
from neoclient.typing import Consumer, Dependency, Function

CS = TypeVar("CS", Callable[..., Any], Type[Service])

DecoratorTarget = Union[Operation, ClientSpecification]
Options = Union[ClientOptions, RequestOptions]


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
        self.consumer(operation)


@dataclass
class ClientDecorator(Decorator):
    consumer: Consumer[ClientSpecification]

    def decorate_client(self, client: ClientSpecification, /) -> None:
        self.consumer(client)


@dataclass
class OptionsDecorator(Decorator):
    consumer: Consumer[Options]

    def decorate_operation(self, operation: Operation, /) -> None:
        return self.consumer(operation.request_options)

    def decorate_client(self, client: ClientSpecification, /) -> None:
        return self.consumer(client.options)


def common_decorator(consumer: Consumer[DecoratorTarget], /):
    return CommonDecorator(consumer)


def operation_decorator(consumer: Consumer[Operation], /):
    return OperationDecorator(consumer)


def client_decorator(consumer: Consumer[ClientSpecification], /):
    return ClientDecorator(consumer)


def client_options_decorator(consumer: Consumer[ClientOptions], /):
    def get_client_options(target: DecoratorTarget, /) -> ClientOptions:
        if isinstance(target, ClientSpecification):
            return target.options
        elif isinstance(target, Operation):
            return target.client_options
        else:
            raise TypeError

    @common_decorator
    def decorate(target: DecoratorTarget, /) -> None:
        client_options: ClientOptions = get_client_options(target)

        consumer(client_options)

    return decorate


def request_options_decorator(consumer: Consumer[RequestOptions], /):
    @operation_decorator
    def decorate(operation: Operation, /) -> None:
        consumer(operation.request_options)

    return decorate


def options_decorator(consumer: Consumer[Options], /):
    return OptionsDecorator(consumer)


def headers_decorator(consumer: Consumer[Headers], /):
    @options_decorator
    def decorate(options: Options, /) -> None:
        consumer(options.headers)

    return decorate


def params_decorator(consumer: Function[QueryParams, QueryParams], /):
    @options_decorator
    def decorate(options: Options, /) -> None:
        options.params = consumer(options.params)

    return decorate


def cookies_decorator(consumer: Consumer[Cookies], /):
    @options_decorator
    def decorate(options: Options, /) -> None:
        consumer(options.cookies)

    return decorate


def middleware_decorator(consumer: Consumer[Middleware], /):
    @common_decorator
    def decorate(target: DecoratorTarget, /) -> None:
        consumer(target.middleware)

    return decorate


def request_dependencies_decorator(consumer: Consumer[MutableSequence[Dependency]], /):
    @common_decorator
    def decorate(target: DecoratorTarget, /) -> None:
        consumer(target.request_dependencies)

    return decorate


def response_dependencies_decorator(consumer: Consumer[MutableSequence[Dependency]], /):
    @common_decorator
    def decorate(target: DecoratorTarget, /) -> None:
        consumer(target.response_dependencies)

    return decorate
