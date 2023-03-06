from enum import auto
from typing import Sequence

from ..enums import HiddenValueEnum

__all__: Sequence[str] = ("Annotation",)


class Annotation(HiddenValueEnum):
    MIDDLEWARE = auto()
    RESPONSE = auto()
