from typing import List, Optional, Protocol
from dataclasses import dataclass

from fastclient import FastClient, get


@dataclass
class Repository:
    id: int
    name: str
    description: Optional[str]


class GitHubService(Protocol):
    @get("users/{user}/repos")
    def list_repos(self, user: str) -> List[Repository]:
        ...


client: FastClient = FastClient("https://api.github.com/")

service: GitHubService = client.create(GitHubService)

repositories: List[Repository] = service.list_repos("octocat")  # type: ignore

repository: Repository
for repository in repositories:
    print(repository)
