# retrofit
HTTP client for Python inspired by [Retrofit](https://square.github.io/retrofit/)

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
    def list_repos(user: str = Path("user")) -> List<Repository>:
        ...
```

The `Retrofit` class generates an implementation of the `GitHubService` protocol.
```python
from retrofit import Retrofit

retrofit: Retrofit = Retrofit("https://api.github.com/")

service: GitHubService = retrofit.create(GitHubService)
```

Each method call of the created `GitHubService` makes a synchronous HTTP request to the remote webserver.
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
