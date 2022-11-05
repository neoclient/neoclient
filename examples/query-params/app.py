from typing import Mapping

from client import echo

response: Mapping[str, str] = echo({"name": "sam", "age": "43"})

print(response)
