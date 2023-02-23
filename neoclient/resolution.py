from typing import Any, Callable

from httpx import Response

from .dependencies import DependencyParameter


def resolve(func: Callable, response: Response) -> Any:
    dependency: DependencyParameter = DependencyParameter(dependency=func)

    return dependency.resolve(response)
