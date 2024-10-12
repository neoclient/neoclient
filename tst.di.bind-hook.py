from inspect import Parameter
from typing import Any, Optional

from di import Container, bind_by_type
from di.api.dependencies import DependentBase
from di.dependent import Dependent
from di.executors import SyncExecutor


def bind_hook(
    param: Optional[Parameter], dependent: DependentBase[Any]
) -> Optional[DependentBase[Any]]:
    print("bind hook called", param, dependent)
    # if param is not None and param.name == "name":
    #     return Dependent(lambda: "Name!", scope=None)
    return None


def dependent(name: str) -> str:
    return f"Hello, {name}"


container = Container()

container.bind(bind_hook)
container.bind(bind_by_type(Dependent(lambda: "psyche!"), str))

executor = SyncExecutor()
solved = container.solve(Dependent(dependent), scopes=(None,))

with container.enter_scope(None) as state:
    d = solved.execute_sync(
        executor=executor,
        state=state,
        # values={Response: response},
    )
