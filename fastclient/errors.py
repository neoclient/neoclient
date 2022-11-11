from typing import Sequence


__all__: Sequence[str] = (
    "DuplicateParameters",
    "IncompatiblePathParameters",
    "PreparationError",
    "CompositionError",
    "ResolutionError",
)

class DuplicateParameters(Exception):
    pass


class IncompatiblePathParameters(Exception):
    pass


class PreparationError(Exception):
    pass


class CompositionError(Exception):
    pass


class ResolutionError(Exception):
    pass
