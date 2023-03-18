from typing import Sequence

from annotate import Annotation

from .enums import Entity

__all__: Sequence[str] = (
    "service_middleware",
    "service_response",
)

service_middleware: Annotation = Annotation(Entity.MIDDLEWARE)
service_response: Annotation = Annotation(Entity.RESPONSE)
