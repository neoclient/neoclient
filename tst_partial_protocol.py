from typing import Protocol, Any

class Resolver(Protocol):
    def __call__(self, param: str) -> Any:
        ...

def standard_resolver(param: str) -> str:
    return param

def partial_resolver(param: str, *, other: str) -> Any:
    return param + "_" + other

sr: Resolver = standard_resolver
pr: Resolver = partial_resolver