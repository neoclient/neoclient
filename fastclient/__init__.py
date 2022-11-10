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

__version__: str = "0.1.3"

from .client import FastClient
from .decorators import content
from .decorators import cookie
from .decorators import cookies
from .decorators import data
from .decorators import files
from .decorators import header
from .decorators import headers
from .decorators import json
from .decorators import path
from .decorators import path_params
from .decorators import query
from .decorators import query_params
from .decorators import timeout
from .methods import delete
from .methods import get
from .methods import head
from .methods import options
from .methods import patch
from .methods import post
from .methods import put
from .methods import request
from .param_functions import URL
from .param_functions import Body
from .param_functions import Cookie
from .param_functions import Cookies
from .param_functions import Depends
from .param_functions import Header
from .param_functions import Headers
from .param_functions import Path
from .param_functions import Paths
from .param_functions import Queries
from .param_functions import Query
from .param_functions import Request
from .param_functions import Response
from .param_functions import StatusCode
