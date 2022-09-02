from dataclasses import dataclass
from http import HTTPStatus

import httpx

from .param_functions import Cookies, Headers, Promise


@dataclass
class HeaderResponse:
    name: str

    def __call__(self, headers: dict = Headers()) -> str:
        return headers[self.name]


@dataclass
class CookieResponse:
    name: str

    def __call__(self, cookies: dict = Cookies()) -> str:
        return cookies[self.name]


def status(response: httpx.Response = Promise()) -> HTTPStatus:
    return HTTPStatus(response.status_code)


def status_code(response: httpx.Response = Promise()) -> int:
    return response.status_code


def status_phrase(response: httpx.Response = Promise()) -> str:
    return HTTPStatus(response.status_code).phrase


def status_name(response: httpx.Response = Promise()) -> str:
    return HTTPStatus(response.status_code).name


def status_description(response: httpx.Response = Promise()) -> str:
    return HTTPStatus(response.status_code).description


def text(response: httpx.Response = Promise()) -> str:
    return response.text


def content(response: httpx.Response = Promise()) -> bytes:
    return response.content


def is_success(response: httpx.Response = Promise()) -> bool:
    return response.is_success
