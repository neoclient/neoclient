import enum


class HttpMethod(str, enum.Enum):
    PUT: str = "PUT"
    GET: str = "GET"
    POST: str = "POST"
    HEAD: str = "HEAD"
    PATCH: str = "PATCH"
    DELETE: str = "DELETE"
    OPTIONS: str = "OPTIONS"
    

class Annotation(enum.Enum):
    SPECIFICATION = enum.auto()