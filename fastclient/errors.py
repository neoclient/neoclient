from dataclasses import dataclass
from typing import Any, Sequence


__all__: Sequence[str] = (
    "DuplicateParameters",
    "IncompatiblePathParameters",
    "PreparationError",
    "CompositionError",
    "ResolutionError",
    "ConversionError",
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


@dataclass
class ConversionError(Exception):
    subject: str
    value: Any

    def __str__(self) -> str:
        return f"Cannot convert {self.subject} from type {type(self.value)}"
