from ._headers import *
from .old_api import CommonDecorator, OperationDecorator, ServiceDecorator
from ._auth import auth, basic_auth
from ._client import base_url
from .common import (
    cookie,
    cookies,
    follow_redirects,
    header,
    headers,
    query,
    query_params,
    request_depends,
    response_depends,
    timeout,
    verify,
)
from ._middleware import (
    expect_content_type,
    expect_header,
    expect_status,
    middleware,
    raise_for_status,
)
from .operation import content, data, files, json, mount, path, path_params
from .request import delete, get, head, options, patch, post, put, request
from .response import response
from .service import service
from .utils import persist_pre_request
