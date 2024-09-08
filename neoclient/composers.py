from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence, TypeAlias, Union

from httpx import QueryParams
from neoclient import converters
from neoclient.models import ClientOptions, RequestOptions
from neoclient.operation import Operation
from neoclient.specification import ClientSpecification
from neoclient.types import QueryTypes

"""

"""

CompositionTarget: TypeAlias = Union[
    RequestOptions, ClientOptions, Operation, ClientSpecification
]


class CompositionError(Exception):
    @classmethod
    def not_supported(cls, typ: type, /) -> "CompositionError":
        return cls(f"{typ.__name__} composition not supported")


class Composer:
    def compose(self, target: CompositionTarget, /) -> None:
        methods = {
            RequestOptions: self.compose_request,
            ClientOptions: self.compose_client,
            Operation: self.compose_operation,
            ClientSpecification: self.compose_client_spec,
        }

        method = methods[type(target)]

        return method(target)

    def compose_request(self, request: RequestOptions, /) -> None:
        raise CompositionError.not_supported(RequestOptions)

    def compose_client(self, client: ClientOptions, /) -> None:
        raise CompositionError.not_supported(ClientOptions)

    def compose_operation(self, operation: Operation, /) -> None:
        raise CompositionError.not_supported(Operation)

    def compose_client_spec(self, client_specification: ClientSpecification, /) -> None:
        raise CompositionError.not_supported(ClientSpecification)


# class RequestComposer(ABC, Composer):
#     @abstractmethod
#     def compose_request(self, request: PreRequest, /) -> None:
#         raise CompositionError.not_supported(PreRequest)

#     def compose_operation(self, operation: Operation, /) -> None:
#         return self.compose_request(operation.pre_request)

#     def compose_client_spec(self, client_specification: ClientSpecification, /) -> None:
#         return self.compose_client(client_specification.options)


def compose(target: CompositionTarget, *composers: Composer) -> None:
    # if isinstance(target, PreRequest):
    #     for composer in composers:
    #         composer.compose_request(target)
    # else:
    raise NotImplementedError

    # methods = {
    #     PreRequest: Composer.compose_request,
    #     ClientOptions: Composer.compose_client,
    #     Operation: Composer.compose_operation,
    #     ClientSpecification: Composer.compose_client_spec,
    # }

    # method = methods[type(target)]

    # composer: Composer
    # for composer in composers:
    #     method(composer, target)


@dataclass(init=False)
class QueryComposer(Composer):
    key: str
    values: Sequence[str]

    def __init__(self, key: str, value: QueryTypes) -> None:
        self.key = key
        self.values = converters.convert_query_param(value)

    def compose_request(self, request: RequestOptions, /) -> None:
        request.params = self._apply(request.params)

    def compose_client(self, client: ClientOptions, /) -> None:
        client.params = self._apply(client.params)

    def _apply(self, params: QueryParams, /) -> QueryParams:
        # If there's only one value, set the query param and overwrite any
        # existing entries for this key
        if len(self.values) == 1:
            return params.set(self.key, self.values[0])

        # Otherwise, update the query params and maintain any existing entries for
        # this key
        value: str
        for value in self.values:
            params = params.add(self.key, value)

        return params
