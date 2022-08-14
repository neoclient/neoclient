import enum

class NoValue(enum.Enum):
    def __repr__(self) -> str:
        return f"<{type(self).__name__}.{self.name}>"


class HttpMethod(str, enum.Enum):
    PUT: str = "PUT"
    GET: str = "GET"
    POST: str = "POST"
    HEAD: str = "HEAD"
    PATCH: str = "PATCH"
    DELETE: str = "DELETE"
    OPTIONS: str = "OPTIONS"


class Annotation(NoValue):
    SPECIFICATION = enum.auto()

class FieldType(NoValue):
    QUERY = enum.auto()
    PATH = enum.auto()
    HEADER = enum.auto()