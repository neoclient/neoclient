from di import Container, bind_by_type
from di.dependent import Dependent
from di.executors import SyncExecutor

from neoclient.models import RequestOpts

request = RequestOpts("GET", "/", headers={"origin": "Request!"})

container = Container()
container.bind(bind_by_type(Dependent(RequestOpts, wire=False), RequestOpts))


def my_dependency(request: RequestOpts, /) -> RequestOpts:
    return request


executor = SyncExecutor()


solved = container.solve(Dependent(my_dependency), scopes=(None,))

with container.enter_scope(None) as state:
    d = solved.execute_sync(
        executor=executor,
        state=state,
        values={RequestOpts: request},
    )

print(repr(d))
