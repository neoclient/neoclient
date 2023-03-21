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

__version__: str = "0.1.27"

from .client import NeoClient
from .decorators import (
    accept,
    base_url,
    content,
    cookie,
    cookies,
    data,
    files,
    header,
    headers,
    json,
    middleware,
    mount,
    path,
    path_params,
    query,
    query_params,
    referer,
    response,
    service,
    timeout,
    user_agent,
    verify,
)
from .methods import delete, get, head, options, patch, post, put, request
from .models import Request, Response
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
    Req,
    Resp,
    State,
    StatusCode,
)
from .service import Service
