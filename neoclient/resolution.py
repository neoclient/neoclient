from typing import Any, Callable

from .dependence import DependencyParameter
from .models import Response


def resolve(func: Callable, response: Response) -> Any:
    dependency: DependencyParameter = DependencyParameter(dependency=func)

    return dependency.resolve_response(response)
