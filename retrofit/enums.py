import enum


class HttpMethod(str, enum.Enum):
    # def __str__(self):
    #     return str.__str__(self)

    GET: str = "GET"
