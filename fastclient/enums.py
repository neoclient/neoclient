import enum


class NoValue(enum.Enum):
    def __repr__(self) -> str:
        return f"<{type(self).__name__}.{self.name}>"


class HttpMethod(NoValue):
    PUT = enum.auto()
    GET = enum.auto()
    POST = enum.auto()
    HEAD = enum.auto()
    PATCH = enum.auto()
    DELETE = enum.auto()
    OPTIONS = enum.auto()


class Annotation(NoValue):
    SPECIFICATION = enum.auto()


class ParamType(NoValue):
    QUERY = enum.auto()
    HEADER = enum.auto()
    PATH = enum.auto()
    COOKIE = enum.auto()

    BODY = enum.auto()

    # TODO: Implement
    # FIELD = enum.auto()
    # PART = enum.auto()
    # FORM = enum.auto()
