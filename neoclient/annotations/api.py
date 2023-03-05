from typing import Any, Sequence

from .constants import ATTRIBUTE_ANNOTATIONS
from .datastructures import Annotations
from .enums import Annotation
from .exceptions import AnnotationException

__all__: Sequence[str] = (
    "has_annotation",
    "add_annotation",
)


def _has_annotations(obj: Any, /) -> bool:
    return hasattr(obj, ATTRIBUTE_ANNOTATIONS)


def _set_annotations(obj: Any, annotations: Annotations, /) -> None:
    setattr(obj, ATTRIBUTE_ANNOTATIONS, annotations)


def _get_annotations(obj: Any, /) -> Annotations:
    if not _has_annotations(obj):
        raise AnnotationException(f"obj {obj!r} has no annotations")

    annotations: Any = getattr(obj, ATTRIBUTE_ANNOTATIONS)

    if not isinstance(annotations, Annotations):
        raise AnnotationException(
            f"obj {obj!r} has invalid annotations of type {type(annotations)!r}"
        )

    return annotations


def has_annotation(obj: Any, annotation: Annotation, /) -> bool:
    return _has_annotations(obj) and annotation in _get_annotations(obj)


def add_annotation(obj: Any, annotation: Annotation, /) -> None:
    if not _has_annotations(obj):
        _set_annotations(obj, Annotations())

    annotations: Annotations = _get_annotations(obj)

    annotations.add(annotation)
