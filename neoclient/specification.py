from dataclasses import dataclass, field
from typing import Any, Callable, MutableSequence, Optional, Sequence

from .middleware import Middleware
from .models import ClientOptions

__all__: Sequence[str] = ("ClientSpecification",)


@dataclass
class ClientSpecification:
    options: ClientOptions = field(default_factory=ClientOptions)
    middleware: Middleware = field(default_factory=Middleware)
    default_response: Optional[Callable[..., Any]] = None
    dependencies: MutableSequence[Callable[..., Any]] = field(default_factory=list)
