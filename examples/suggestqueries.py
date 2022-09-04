from typing import Optional, Protocol

from fastclient import FastClient, Query, get, params


class SuggestQueries(Protocol):
    @params({"xhr": "t", "hjson": "t"})
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
# > [
# >     'foo',
# >     [
# >         ['football scores', 0, [512, 433, 131]],
# >         ['football today', 0, [512, 433, 131]],
# >         ['football results', 0, [512, 433, 131]],
# >         ['food near me', 0, [512, 457]],
# >         ['footlocker', 0, [512, 433]],
# >         ['football fixtures', 0, [512, 433, 131]],
# >         ['football on tv', 0, [512, 433, 131]],
# >         ['football', 0, [512, 433, 131]],
# >         ['food', 0, [512, 433, 131]],
# >         ['football scores today', 0, [512, 433, 131]],
# >         ['footasylum', 0, [512, 433]],
# >         ['football news', 0, [512, 433, 131]],
# >         ['football tables', 0, [512, 433, 131]],
# >         ['football fixtures today', 0, [512, 433, 131]]
# >     ],
# >     {'k': 1, 'q': 'DeMQLRH9I9y29EDH7UjVnB758sU'}
# > ]
