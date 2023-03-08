from typing import Any, List, Mapping, Optional, NamedTuple

from neoclient import Query, Service, base_url, get, query_params


class Suggestion(NamedTuple):
    suggestion: str
    location: int
    confidence: List[int]


class Response(NamedTuple):
    query: str
    suggestions: List[Suggestion]
    parameters: Mapping[str, Any]


@base_url("https://suggestqueries.google.com/")
class SuggestQueries(Service):
    @query_params({"xhr": "t", "hjson": "t"})
    @get("/complete/search")
    def complete_search(
        self,
        query: str = Query("q"),
        /,
        *,
        client: str,
        datasource: Optional[str] = None,
    ) -> Response:
        ...


suggest_queries: SuggestQueries = SuggestQueries()

response: Response = suggest_queries.complete_search(
    "foo", client="youtube", datasource="yt"
)

for suggestion in response.suggestions:
    print(suggestion.suggestion)
