from fastclient.methods import request
from fastclient.models import RequestOptions, OperationSpecification
from fastclient.param_functions import Query
from fastclient.enums import Annotation
from typing import Protocol
import annotate


def test_request_no_url() -> None:
    class Service(Protocol):
        @request("GET")
        def operation(self, param: str = Query("param")) -> RequestOptions:
            ...

    assert annotate.get_annotations(Service.operation) == {
        Annotation.SPECIFICATION: OperationSpecification(
            request=RequestOptions(method="GET", url="operation"),
            params={"param": Query("param")},
        )
    }
