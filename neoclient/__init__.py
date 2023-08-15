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

__version__: str = "0.1.47"

from .client import NeoClient
from .decorators import (
    accept,
    base_url,
    content,
    cookie,
    cookies,
    data,
    files,
    follow_redirects,
    header,
    headers,
    json,
    mount,
    path,
    path_params,
    query,
    query_params,
    referer,
    request_depends,
    response,
    response_depends,
    service,
    timeout,
    user_agent,
    verify,
)
from .decorators.middleware import (
    expect_content_type,
    expect_header,
    expect_status,
    middleware,
    raise_for_status,
)
from .decorators.request import delete, get, head, options, patch, post, put, request
from .models import PreRequest, Request, Response
from .param_functions import (
    URL,
    Body,
    Cookie,
    Cookies,
    Depends,
    Header,
    Headers,
    Path,
    PathParams,
    Query,
    QueryParams,
    Reason,
    State,
    StatusCode,
)
from .services import Service
