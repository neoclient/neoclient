"""
Decorators are made of 2x things:
1. A "sourcer" - acts like a funnel, takes an Operation/Client
  and turns it into the thing you *actually* care about
2. A "consumer" - applies the decoration
"""

from typing import Generic, TypeVar, Union

from httpx import Headers

from neoclient.decorators.api import DecoratorTarget, common_decorator
from neoclient.operation import Operation
from neoclient.specification import ClientSpecification
from neoclient.typing import Consumer


# T = TypeVar("T")


# class SourcerException(Exception):
#     pass


# class Sourcer(Generic[T]):
#     def from_operation(self, operation: Operation, /) -> T:
#         raise SourcerException("Sourcing from operation not supported")

#     def from_client(self, client: ClientSpecification, /) -> T:
#         raise SourcerException("Sourcing from client not supported")


# class HeaderSourcer(Sourcer[Headers]):
#     def from_operation(self, operation: Operation, /) -> Headers:
#         return operation.headers

#     def from_client(self, client: ClientSpecification, /) -> Headers:
#         return client.headers

def headers_decorator(consumer: Consumer[Headers], /):
    @common_decorator
    def decorate(target: DecoratorTarget, /) -> None:
        consumer(target.headers)
    
    return decorate


def referer(referer: str, /):
    @headers_decorator
    def decorate(headers: Headers, /) -> None:
        headers["referer"] = referer

    return decorate
