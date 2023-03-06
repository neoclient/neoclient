from typing import Sequence, Set

from .enums import Annotation

__all__: Sequence[str] = ("Annotations",)


class Annotations(Set[Annotation]):
    pass
