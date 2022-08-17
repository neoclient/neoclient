# retrofit
HTTP client for Python inspired by [FastAPI](https://github.com/tiangolo/fastapi) and [Retrofit](https://square.github.io/retrofit/)

## Introduction
Retrofit turns your HTTP API into a Python protocol.
```python
from retrofit import get, Path
from typing import Protocol
from dataclasses import dataclass

@dataclass
class Repository:
    id: int
    name: str
    description: str

class GitHubService(Protocol):
    @get("users/{user}/repos")
    def list_repos(user: str = Path("user")) -> List[Repository]:
        ...
```

The `Retrofit` class generates an implementation of the `GitHubService` protocol.
```python
from retrofit import Retrofit

retrofit: Retrofit = Retrofit("https://api.github.com/")

service: GitHubService = retrofit.create(GitHubService)
```

Each method call to the created `GitHubService` makes a synchronous HTTP request to the remote webserver.
```python
from typing import List

repos: List[Repository] = service.list_repos("octocat")
```
```python
>>> repos[0]
Repository(id=132935648, name="boysenberry-repo-1", description="Testing")
```

Use annotations to describe the HTTP request:
* URL parameter replacement and query parameter support
* Object conversion to request body (e.g., JSON)
* Multipart request body and file upload

## API Declaration
Annotations on the protocol methods and default parameter values indicate how a request will be handled.

### Request Method
Every method must have an HTTP annotation that provides the request method and an optional URL/URI. There are eight built-in annotations: `http`, `get`, `post`, `put`, `patch`, `delete`, `options` and `head`. The URL/URI of the resource is specified in the annotation and is inferred from the method name if not provided.
```python
@get("users/list")
```

You can also specify query parameters in the URL.
```python
@get("users/list?sort=desc")
```

### URL Manipulation
A request URL can be updated dynamically using replacement blocks and parameters on the method. A replacement block is an alphanumeric string surrounded by `{` and `}`. A corresponding parameter must be defined with a default value of type `Path`.
```python
@get("group/{id}/users")
def group_list(group_id: int = Path("id")) -> List[User]:
    ...
```

Query parameters can also be added.
```python
@get("group/{id}/users")
def group_list(group_id: int = Path("id"), sort: str = Query("sort")) -> List[User]:
    ...
```

For complex query parameter combinations a `dict` can be used.
```python
@get("group/{id}/users")
def group_list(group_id: int = Path("id"), options: Dict[str, str] = QueryDict()) -> List[User]:
    ...
```