from dataclasses import dataclass
from httpx import QueryParams
from di import Container
from di.dependent import Dependent
from di.executors import SyncExecutor


class A: ...


class B: ...


@dataclass
class C:
    a: A
    b: B


def main():
    container = Container()
    executor = SyncExecutor()
    solved = container.solve(Dependent(C, scope="request"), scopes=["request"])
    with container.enter_scope("request") as state:
        c = solved.execute_sync(executor=executor, state=state)
    assert isinstance(c, C)
    assert isinstance(c.a, A)
    assert isinstance(c.b, B)
