from typing import Mapping

from client import perform

response: Mapping[str, str] = perform(
    {
        "action": "destroy",
        "item": "castle",
        "time": "now",
    }
)

print(response)
