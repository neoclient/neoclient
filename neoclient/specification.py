from dataclasses import dataclass, field
from typing import MutableSequence, Optional, Sequence

from .middlewares import Middleware
from .models import ClientOptions
from .typing import Dependency

__all__: Sequence[str] = ("ClientSpecification",)


@dataclass
class ClientSpecification:
    options: ClientOptions = field(default_factory=ClientOptions)
    middleware: Middleware = field(default_factory=Middleware)
    default_response: Optional[Dependency] = None
    request_dependencies: MutableSequence[Dependency] = field(default_factory=list)
    response_dependencies: MutableSequence[Dependency] = field(default_factory=list)
