from retrofit.annotators import request
from retrofit.models import Query, Specification
from retrofit.enums import Annotation
from typing import Protocol
import annotate


def test_request_no_endpoint() -> None:
    class Service(Protocol):
        @request("GET")
        def operation(param: str = Query("param")):
            ...

    assert annotate.get_annotations(Service.operation) == {
        Annotation.SPECIFICATION: Specification(
            method="GET", endpoint="operation", fields={"param": Query("param")}
        )
    }
