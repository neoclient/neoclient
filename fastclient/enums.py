import enum


class HiddenValue(enum.Enum):
    def __repr__(self) -> str:
        return f"<{type(self).__name__}.{self.name}>"


class HttpMethod(str, HiddenValue):
    def __str__(self) -> str:
        return self.value

    PUT = "PUT"
    GET = "GET"
    POST = "POST"
    HEAD = "HEAD"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"


# class Annotation(HiddenValue):
#     OPERATION = enum.auto()


class ParamType(HiddenValue):
    QUERY = enum.auto()
    HEADER = enum.auto()
    PATH = enum.auto()
    COOKIE = enum.auto()
    BODY = enum.auto()
