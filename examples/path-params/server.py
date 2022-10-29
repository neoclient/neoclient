from typing import Sequence
from pathlib import Path
from fastapi import FastAPI

app: FastAPI = FastAPI()


@app.get("/{path_params:path}")
def echo(path_params: Path) -> Sequence[str]:
    return path_params.parts
