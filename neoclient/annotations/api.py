from typing import Any, Sequence

from .constants import ATTRIBUTE_ANNOTATIONS
from .datastructures import Annotations
from .enums import Annotation
from .exceptions import AnnotationException

__all__: Sequence[str] = (
    "has_annotations",
    "set_annotations",
    "get_annotations",
    "has_annotation",
    "add_annotation",
)


def has_annotations(obj: Any, /) -> bool:
    return hasattr(obj, ATTRIBUTE_ANNOTATIONS)


def set_annotations(obj: Any, annotations: Annotations, /) -> None:
    setattr(obj, ATTRIBUTE_ANNOTATIONS, annotations)


def get_annotations(obj: Any, /) -> Annotations:
    if not has_annotations(obj):
        raise AnnotationException(f"obj {obj!r} has no annotations")

    annotations: Any = getattr(obj, ATTRIBUTE_ANNOTATIONS)

    if not isinstance(annotations, Annotations):
        raise AnnotationException(
            f"obj {obj!r} has invalid annotations of type {type(annotations)!r}"
        )

    return annotations


def has_annotation(obj: Any, annotation: Annotation, /) -> bool:
    return has_annotations(obj) and annotation in get_annotations(obj)


def add_annotation(obj: Any, annotation: Annotation, /) -> None:
    if not has_annotations(obj):
        set_annotations(obj, Annotations())

    annotations: Annotations = get_annotations(obj)

    annotations.add(annotation)
