from dataclasses import dataclass
from typing import List, Optional

from neoclient import Service, base_url, get


@dataclass
class Repository:
    id: int
    name: str
    description: Optional[str]


@base_url("https://api.github.com/")
class GitHub(Service):
    @get("users/{user}/repos")
    def list_repos(self, user: str) -> List[Repository]: ...


service: GitHub = GitHub()

repositories: List[Repository] = service.list_repos("octocat")

repository: Repository
for repository in repositories:
    print(repository)
