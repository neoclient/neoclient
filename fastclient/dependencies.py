from dataclasses import dataclass
from typing import Any, Callable, MutableMapping, Optional, TypeVar

from httpx import Response
from pydantic.fields import ModelField

from .errors import ResolutionError, PreparationError
from .params import Parameter
from .resolution.api import resolve
from .typing import Resolver

T = TypeVar("T")


@dataclass
class DependencyResolver(Resolver[T]):
    dependency: Callable[..., T]

    def __call__(self, response: Response, /) -> T:
        return resolve(self.dependency, response)


@dataclass
class DependencyParameter(Parameter):
    dependency: Optional[Callable] = None
    use_cache: bool = True

    def resolve(
        self,
        response: Response,
        /,
        *,
        cached_dependencies: Optional[MutableMapping[Callable, Any]] = None,
    ) -> Any:
        if self.dependency is None:
            raise ResolutionError(
                f"Cannot resolve parameter {type(self)!r} without a dependency"
            )

        if cached_dependencies is None:
            cached_dependencies = {}

        if self.use_cache and self.dependency in cached_dependencies:
            return cached_dependencies[self.dependency]

        resolved: Any = DependencyResolver(self.dependency)(response)

        # Cache resolved dependency
        cached_dependencies[self.dependency] = resolved

        return resolved

    def prepare(self, field: ModelField, /) -> None:
        if self.dependency is None:
            if not callable(field.annotation):
                raise PreparationError(
                    f"Failed to prepare parameter: {self!r}. Dependency has non-callable annotation"
                )

            self.dependency = field.annotation
