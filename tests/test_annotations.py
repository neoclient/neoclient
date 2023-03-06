from neoclient.annotations import api
from neoclient.annotations.constants import ATTRIBUTE_ANNOTATIONS
from neoclient.annotations.datastructures import Annotations
from neoclient.annotations.enums import Annotation


def test_api_has_annotation() -> None:
    def foo() -> None:
        pass

    api.set_annotations(foo, Annotations((Annotation.MIDDLEWARE,)))

    assert api.has_annotation(foo, Annotation.MIDDLEWARE)
    assert not api.has_annotation(foo, Annotation.RESPONSE)


def test_api_add_annotation() -> None:
    def foo() -> None:
        pass

    api.add_annotation(foo, Annotation.MIDDLEWARE)

    assert api.get_annotations(foo) == {Annotation.MIDDLEWARE}

    api.add_annotation(foo, Annotation.RESPONSE)

    assert api.get_annotations(foo) == {Annotation.MIDDLEWARE, Annotation.RESPONSE}

    api.add_annotation(foo, Annotation.RESPONSE)

    assert api.get_annotations(foo) == {Annotation.MIDDLEWARE, Annotation.RESPONSE}
