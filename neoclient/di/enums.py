from enum import Enum, auto


class Profile(Enum):
    # The "request" profile is for dependencies working with the pre-request
    # object (RequestOpts).
    # These dependencies are used during the "composition" stage.
    REQUEST = auto()

    # The "response" profile is for dependencies dealing with a `Response`,
    # and therefore by extension a `Request`.
    # These dependencies are used during the "resolution" stage.
    RESPONSE = auto()
