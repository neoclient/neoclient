from dataclasses import dataclass
from typing import Any, Optional, Sequence

__all__: Sequence[str] = (
    "DuplicateParameters",
    "IncompatiblePathParameters",
    "PreparationError",
    "CompositionError",
    "ResolutionError",
    "ConversionError",
    "NotAnOperationError",
    "ExpectedStatusCodeError",
    "ExpectedHeaderError",
    "MissingStateError",
    "ServiceInitialisationError",
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


class NotAnOperationError(Exception):
    pass


class ExpectedStatusCodeError(Exception):
    pass


@dataclass
class ExpectedHeaderError(Exception):
    name: str
    value: Optional[str] = None
    expected_value: Optional[str] = None

    def __str__(self) -> str:
        if self.value is None:
            return f"Response missing expected header {str(self.name)!r}"

        return (
            f"Response header {str(self.name)!r} has incorrect value."
            f" Expected {self.expected_value!r}, got {self.value!r}"
        )


@dataclass
class MissingStateError(Exception):
    key: str

    def __str__(self) -> str:
        return f"State entry missing for key {self.key!r}"


class ServiceInitialisationError(Exception):
    pass
