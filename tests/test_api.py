from retrofit.annotators import request
from retrofit.models import Specification
from retrofit.param_functions import Query
from retrofit.enums import Annotation
from typing import Protocol
import annotate


def test_request_no_url() -> None:
    class Service(Protocol):
        @request("GET")
        def operation(self, param: str = Query("param")):
            ...

    assert annotate.get_annotations(Service.operation) == {
        Annotation.SPECIFICATION: Specification(
            method="GET", url="operation", fields={"param": Query("param")}
        )
    }
