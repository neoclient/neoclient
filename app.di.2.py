from di import Container, bind_by_type
from di.dependent import Dependent
from di.executors import SyncExecutor
from httpx import Request, Headers, Response

request = Request("GET", "/", headers={"origin": "Request!"})
response = Response(200, headers={"origin": "Response!"})


def extract_request(response: Response, /) -> Request:
    return response.request


def extract_headers_from_request(request: Request, /) -> Headers:
    return request.headers


def extract_headers_from_response(response: Response, /) -> Headers:
    return response.headers


def extract_origin(headers: Headers, /) -> str:
    return headers["origin"]


def build_request_container() -> Container:
    container = Container()

    container.bind(bind_by_type(Dependent(Request, wire=False), Request))

    container.bind(bind_by_type(Dependent(extract_headers_from_request), Headers))

    return container


def build_response_container() -> Container:
    container = Container()

    container.bind(bind_by_type(Dependent(Response, wire=False), Response))
    container.bind(bind_by_type(Dependent(extract_request), Request))

    container.bind(bind_by_type(Dependent(extract_headers_from_response), Headers))

    return container


container = build_response_container()

# container.bind(bind_by_type(Dependent(extract_headers_from_request, scope="request"), Headers))
# container.bind(bind_by_type(Dependent(extract_headers_from_response, scope="response"), Headers))
# container.bind(bind_by_type(Dependent(Request, wire=False, scope="request"), Request))
# container.bind(bind_by_type(Dependent(extract_request, scope="response"), Request))

executor = SyncExecutor()

# solved = container.solve(Dependent(extract_origin), scopes=("request", "response"))
solved = container.solve(Dependent(extract_origin), scopes=(None,))

# with container.enter_scope("response") as state:
with container.enter_scope(None) as state:
    origin = solved.execute_sync(
        # executor=executor, state=state, values={Request: request}
        executor=executor,
        state=state,
        values={Response: response},
    )

print(origin)
