import enum
from typing import Literal
from typing_extensions import TypeAlias

class Sentinel(enum.Enum):
    Missing = enum.auto()

MissingType: TypeAlias = Literal[Sentinel.Missing]

Missing: MissingType = Sentinel.Missing
