from typing import Any, Callable

from .dependencies import DependencyParameter
from .models import Response


def resolve(func: Callable, response: Response) -> Any:
    dependency: DependencyParameter = DependencyParameter(dependency=func)

    return dependency.resolve(response)
