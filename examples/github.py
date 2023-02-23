from dataclasses import dataclass
from typing import List, Optional, Protocol

from neoclient import NeoClient, get


@dataclass
class Repository:
    id: int
    name: str
    description: Optional[str]


class GitHubService(Protocol):
    @get("users/{user}/repos")
    def list_repos(self, user: str) -> List[Repository]:
        ...


client: NeoClient = NeoClient("https://api.github.com/")

service: GitHubService = client.create(GitHubService)  # type: ignore

repositories: List[Repository] = service.list_repos("octocat")

repository: Repository
for repository in repositories:
    print(repository)
