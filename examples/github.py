from retrofit import Retrofit, Path, get
from typing import List, Protocol
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

from retrofit import Retrofit

retrofit: Retrofit = Retrofit("https://api.github.com/")

service: GitHubService = retrofit.create(GitHubService)

repos: List[Repository] = service.list_repos("octocat")

repo: Repository
for repo in repos:
    print(repo)