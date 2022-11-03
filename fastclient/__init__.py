__version__: str = "0.1.0"

from .client import FastClient
from .composition.decorators import (
    content,
    cookie,
    cookies,
    data,
    files,
    header,
    headers,
    json,
    path,
    path_params,
    query,
    query_params,
    timeout,
)
from .methods import delete, get, head, options, patch, post, put, request
from .models import Client
from .parameter_functions import (
    URL,
    Body,
    Cookie,
    Cookies,
    Depends,
    Header,
    Headers,
    Path,
    Paths,
    Queries,
    Query,
    Request,
    Response,
    StatusCode,
)
