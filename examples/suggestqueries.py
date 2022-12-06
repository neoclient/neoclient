from typing import Optional, Protocol

from rich.pretty import pprint

from neoclient import NeoClient, Query, get, query_params


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


client: NeoClient = NeoClient("https://suggestqueries.google.com/")

suggest_queries: SuggestQueries = client.create(SuggestQueries)  # type: ignore

results: list = suggest_queries.complete_search(
    "foo", client="youtube", datasource="yt"
)

pprint(results)
