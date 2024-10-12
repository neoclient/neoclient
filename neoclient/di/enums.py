from enum import Enum, auto


class Profile(Enum):
    # The "request" profile is for dependencies working with the pre-request
    # object (RequestOpts).
    REQUEST = auto()

    # The "response" profile is for dependencies dealing with a `Response`,
    # and therefore by extension a `Request`.
    RESPONSE = auto()
