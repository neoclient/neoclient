from neoclient import Headers
from httpx import _types

# Would like this API, though then `Headers` has a name conflict
headers: Headers = Headers({"name": "sam"})