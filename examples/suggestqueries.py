from typing import Optional, Protocol

from fastclient import FastClient, Query, get, query_params
from rich.pretty import pprint


class SuggestQueries(Protocol):
    @query_params({"xhr": "t", "hjson": "t"})
    @get("/complete/search")
    def complete_search(
        self,
        query: str = Query(alias="q"),
        /,
        *,
        client: str,
        datasource: Optional[str] = None,
    ) -> list:
        ...


fastclient: FastClient = FastClient("https://suggestqueries.google.com/")

suggest_queries: SuggestQueries = fastclient.create(SuggestQueries)  # type: ignore

results: list = suggest_queries.complete_search(
    "foo", client="youtube", datasource="yt"
)

pprint(results)