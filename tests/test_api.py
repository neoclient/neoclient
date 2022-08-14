from retrofit.api import request
from retrofit.models import Query, RequestSpecification
from retrofit.enums import Annotation
from typing import Protocol
import annotate


def test_request_no_endpoint() -> None:
    class Service(Protocol):
        @request("GET")
        def operation(self, param: Query("param")):
            ...

    assert annotate.get_annotations(Service.operation) == {
        Annotation.SPECIFICATION: RequestSpecification(
            method="GET", endpoint="operation", params={"param": Query("param")}
        )
    }
