r"""
  __           _       _ _            _
 / _| __ _ ___| |_ ___| (_) ___ _ __ | |_
| |_ / _` / __| __/ __| | |/ _ \ '_ \| __|
|  _| (_| \__ \ || (__| | |  __/ | | | |_
|_|  \__,_|___/\__\___|_|_|\___|_| |_|\__|

       Fast API Clients for Python
       ~~~~~~~~~~~~~~~~~~~~~~~~~~~
               @tombulled
"""

__version__: str = "0.1.5"

from .client import FastClient
from .decorators import (
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
from .methods import (
    delete,
    get,
    head,
    options,
    patch,
    post,
    put,
    request,
)
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
