from annotate import Annotation

from .enums import Entity

__all__ = (
    "service_middleware",
    "service_response",
    "service_request_dependency",
    "service_response_dependency",
)

service_middleware: Annotation = Annotation(Entity.MIDDLEWARE)
service_response: Annotation = Annotation(Entity.RESPONSE)
service_request_dependency: Annotation = Annotation(Entity.REQUEST_DEPENDENCY)
service_response_dependency: Annotation = Annotation(Entity.RESPONSE_DEPENDENCY)
