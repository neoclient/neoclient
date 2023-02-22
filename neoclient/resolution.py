from typing import Callable

from httpx import Response

from .dependencies import DependencyParameter


def resolve(func: Callable, response: Response):
    dependency: DependencyParameter = DependencyParameter(dependency=func)

    return dependency.resolve(response)