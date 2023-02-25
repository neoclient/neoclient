from typing import Any, MutableMapping, Optional, Union

import httpx
from neoclient.types import (
    MethodTypes,
    URLTypes,
    HeaderTypes,
    CookieTypes,
    RequestContent,
    RequestData,
    RequestFiles,
    SyncByteStream,
    AsyncByteStream,
    QueriesTypes,
)


class Request(httpx.Request):
    state: MutableMapping[str, Any]

    def __init__(
        self,
        method: MethodTypes,
        url: URLTypes,
        *,
        params: Optional[QueriesTypes] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        content: Optional[RequestContent] = None,
        data: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        json: Optional[Any] = None,
        stream: Union[SyncByteStream, AsyncByteStream, None] = None,
        extensions: Optional[dict] = None,
        state: Optional[MutableMapping[str, Any]] = None,
    ):
        super().__init__(
            method=method,
            url=url,
            params=params,
            headers=headers,
            cookies=cookies,
            content=content,
            data=data,
            files=files,
            json=json,
            stream=stream,
            extensions=extensions,
        )

        if state is not None:
            self.state = state
        else:
            self.state = {}


r = Request("GET", "/foo")
