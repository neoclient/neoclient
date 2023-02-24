r"""
```
                       _ _            _   
 _ __   ___  ___   ___| (_) ___ _ __ | |_ 
| '_ \ / _ \/ _ \ / __| | |/ _ \ '_ \| __|
| | | |  __/ (_) | (__| | |  __/ | | | |_ 
|_| |_|\___|\___/ \___|_|_|\___|_| |_|\__|

       Fast API Clients for Python
       ~~~~~~~~~~~~~~~~~~~~~~~~~~~
               @tombulled
```
"""

__version__: str = "0.1.15"

from .client import NeoClient
from .decorators import (
    content,
    cookie,
    cookies,
    data,
    files,
    header,
    headers,
    json,
    middleware,
    path,
    path_params,
    query,
    query_params,
    timeout,
)
from .methods import delete, get, head, options, patch, post, put, request
from .param_functions import (
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
