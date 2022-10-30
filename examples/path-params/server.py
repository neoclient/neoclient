from typing import Mapping

from fastapi import FastAPI

app: FastAPI = FastAPI()


@app.get("/{action}/{item}/{time}")
def perform(action: str, item: str, time: str) -> Mapping[str, str]:
    return {
        "action": action,
        "item": item,
        "time": time,
    }
