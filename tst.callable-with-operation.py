from dataclasses import dataclass
from typing import Protocol, TypeVar, runtime_checkable
from typing_extensions import ParamSpec

PS = ParamSpec("PS")
RT = TypeVar("RT", covariant=True)


@dataclass
class Request:
    method: str
    path: str


@dataclass
class Specification:
    request: Request


@dataclass
class Operation:
    specification: Specification


operation: Operation = Operation(
    specification=Specification(
        request=Request(
            method="GET",
            path="/",
        ),
    ),
)

def foo():
    pass

def bar():
    pass

setattr(bar, "operation", operation)


@runtime_checkable
class CallableWithOperation(Protocol[PS, RT]):
    operation: "Operation"

    def __call__(self, *args: PS.args, **kwargs: PS.kwargs) -> RT:
        ...

a = isinstance(foo, CallableWithOperation)
b = isinstance(bar, CallableWithOperation)