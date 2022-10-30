from fastclient.composition.composers import compose_query_param
from fastclient.parameters import QueryParameter

d = compose_query_param(QueryParameter(alias="foo"), 123)
# d = compose_query_param(Query(), 123) # missing alias
# d = compose_query_param(Query(alias="foo"), None) # ignorable
