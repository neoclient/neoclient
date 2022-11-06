from dataclasses import dataclass
from typing import Any, Callable, MutableMapping, Optional, TypeVar

from httpx import Response
from pydantic.fields import ModelField

from .errors import ResolutionError
from .parameters import BaseParameter
from .resolution.api import resolve
from .resolution.typing import ResolutionFunction

T = TypeVar("T")


@dataclass
class DependencyResolutionFunction(ResolutionFunction[T]):
    dependency: Callable[..., T]

    def __call__(self, response: Response, /) -> T:
        return resolve(self.dependency, response)


@dataclass
class DependencyParameter(BaseParameter):
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

        resolved: Any = DependencyResolutionFunction(self.dependency)(response)

        # Cache resolved dependency
        cached_dependencies[self.dependency] = resolved

        return resolved

    def prepare(self, field: ModelField, /) -> None:
        super().prepare(field)

        if self.dependency is None:
            if not callable(field.annotation):
                # NOTE: This could also viably be a `CompositionError`, maybe throw a `PreparationError` instead?
                raise ResolutionError(
                    f"Failed to resolve parameter: {self!r}. Dependency has non-callable annotation"
                )

            self.dependency = field.annotation
