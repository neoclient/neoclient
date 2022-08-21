import functools
import inspect
import pydantic
from dataclasses import dataclass
from inspect import Parameter, Signature
from types import FunctionType
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    NoReturn,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
)

import annotate
import furl
import param
import fastapi.encoders
from arguments import Arguments
from httpx import Response
from param import Missing
from pydantic import BaseModel
from typing_extensions import ParamSpec

from . import utils
from .converters import Converter, HttpxResolver, IdentityConverter, Resolver
from .enums import Annotation, HttpMethod, ParamType
from .models import Request, Specification
from .params import Body, Param, Params, Path, Query

T = TypeVar("T")

PT = ParamSpec("PT")
RT = TypeVar("RT")


def get_specification(obj: Any, /) -> Optional[Specification]:
    return annotate.get_annotations(obj).get(Annotation.SPECIFICATION)


def get_specifications(cls: type, /) -> Dict[str, Specification]:
    return {
        member_name: annotate.get_annotations(member)[Annotation.SPECIFICATION]
        for member_name, member in inspect.getmembers(cls)
        if isinstance(member, FunctionType)
        and Annotation.SPECIFICATION in annotate.get_annotations(member)
    }


class BaseService:
    def __repr__(self) -> str:
        return f"<{type(self).__name__}()>"


@dataclass
class FastClient:
    base_url: Optional[str] = None
    resolver: Resolver = HttpxResolver()
    converter: Converter = IdentityConverter()

    def create(self, protocol: Type[T], /) -> T:
        specifications: Dict[str, Specification] = get_specifications(protocol)

        attributes: dict = {"__module__": protocol.__module__}

        func_name: str
        specification: Specification
        for func_name, specification in specifications.items():
            func: FunctionType = getattr(protocol, func_name)

            # Validate url is a fully qualified url if no base url
            if (
                self.base_url is None or not furl.has_netloc(self.base_url)
            ) and not furl.has_netloc(specification.request.url):
                raise Exception(
                    f"Cannot construct fully-qualified URL from: base_url={self.base_url!r}, endpoint={specification.request.url!r}"
                )

            attributes[func_name] = self._method(specification, func)

        return type(protocol.__name__, (BaseService,), attributes)()

    def _url(self, endpoint: str, /) -> str:
        if furl.has_netloc(endpoint):
            return endpoint

        if self.base_url is None or not furl.has_netloc(self.base_url):
            raise Exception(
                f"Cannot construct fully-qualified URL from: base_url={self.base_url!r}, endpoint={endpoint!r}"
            )

        return furl.urljoin(self.base_url, endpoint)

    def _method(
        self, specification: Specification, method: Callable[PT, RT], /
    ) -> Callable[PT, RT]:
        signature: Signature = inspect.signature(method)

        @functools.wraps(method)
        def wrapper(*args: PT.args, **kwargs: PT.kwargs) -> Union[Any, NoReturn]:
            arguments: Dict[str, Any] = Arguments(*args, **kwargs).bind(method).asdict()

            argument_name: str
            argument: Any
            for argument_name, argument in arguments.items():
                if not isinstance(argument, Param):
                    continue

                if not argument.has_default():
                    raise ValueError(
                        f"{method.__name__}() missing argument: {argument_name!r}"
                    )

                arguments[argument_name] = argument.default

            destinations: Dict[ParamType, Dict[str, Any]] = {}

            parameter: str
            field: Param
            for parameter, field in specification.params.items():
                value: Any = arguments[parameter]

                if isinstance(field, Param):
                    field_name: str = (
                        field.alias
                        if field.alias is not None
                        else field.generate_alias(parameter)
                    )

                    # The field is not required, it can be omitted
                    if value is None and not field.required:
                        continue

                    destinations.setdefault(field.type, {})[field_name] = value
                elif isinstance(field, Params):
                    destinations.setdefault(field.type, {}).update(value)
                else:
                    raise Exception(f"Unknown field type: {field}")

            body_params: Dict[str, Any] = destinations.get(ParamType.BODY, {})

            json: Any = None

            # If there's only one body param, make it the entire JSON request body
            if len(body_params) == 1:
                json = fastapi.encoders.jsonable_encoder(list(body_params.values())[0])
            # If there are multiple body params, construct a multi-level dict
            # of each body parameter. E.g. (user: User, item: Item) -> {"user": ..., "item": ...}
            elif body_params:
                json = {key: fastapi.encoders.jsonable_encoder(val) for key, val in body_params.items()}

            request: Request = Request(
                method=specification.request.method,
                url=self._url(specification.request.url).format(
                    **destinations.get(ParamType.PATH, {})
                ),
                params={
                    **specification.request.params,
                    **destinations.get(ParamType.QUERY, {}),
                },
                headers={
                    **specification.request.headers,
                    **destinations.get(ParamType.HEADER, {}),
                },
                cookies={
                    **specification.request.cookies,
                    **destinations.get(ParamType.COOKIE, {}),
                },
                json=json,
            )

            return_annotation: Any = signature.return_annotation

            if return_annotation is Request:
                return request

            response: Response = self.converter.convert(self.resolver.resolve(request))

            if return_annotation is signature.empty:
                return response.json()
            if return_annotation is None:
                return None
            if return_annotation is Response:
                return response
            if isinstance(return_annotation, type) and issubclass(return_annotation, BaseModel):
                return return_annotation.parse_obj(response.json())

            return pydantic.parse_raw_as(return_annotation, response.text)

        return wrapper

    def request(self, method: str, endpoint: Optional[str] = None, /):
        def decorator(func: Callable[PT, RT], /) -> Callable[PT, RT]:
            uri: str = (
                endpoint if endpoint is not None else Path.generate_alias(func.__name__)
            )

            specification: Specification = build_request_specification(
                func,
                method,
                uri,
            )

            return self._method(specification, func)

        return decorator

    def put(self, endpoint: str, /):
        return self.request(HttpMethod.PUT.name, endpoint)

    def get(self, endpoint: str, /):
        return self.request(HttpMethod.GET.name, endpoint)

    def post(self, endpoint: str, /):
        return self.request(HttpMethod.POST.name, endpoint)

    def head(self, endpoint: str, /):
        return self.request(HttpMethod.HEAD.name, endpoint)

    def patch(self, endpoint: str, /):
        return self.request(HttpMethod.PATCH.name, endpoint)

    def delete(self, endpoint: str, /):
        return self.request(HttpMethod.DELETE.name, endpoint)

    def options(self, endpoint: str, /):
        return self.request(HttpMethod.OPTIONS.name, endpoint)

def _build_parameter(parameter: Parameter, spec: Param) -> param.Parameter:
    return param.Parameter(
        name=parameter.name,
        annotation=parameter.annotation,
        type=getattr(param.ParameterType, parameter.kind.name),
        spec=spec,
    )

def _extract_path_params(parameters: Iterable[param.Parameter]) -> Set[str]:
    return {
        (
            parameter.spec.alias
            if parameter.spec.alias is not None
            else parameter.spec.generate_alias(parameter.name)
        )
        for parameter in parameters
        if isinstance(parameter.spec, Path)
    }


def get_params(
    func: Callable, /, *, request: Optional[Request] = None
) -> Dict[str, param.Parameter]:
    path_params: Set[str] = (
        utils.get_path_params(request.url) if request is not None else set()
    )

    raw_parameters: List[Parameter] = list(inspect.signature(func).parameters.values())[
        1:
    ]

    parameters: Dict[str, param.Parameter] = {}
    parameters_to_infer: List[Parameter] = []

    parameter: Parameter

    for parameter in raw_parameters:
        if isinstance(parameter.default, Param):
            parameters[parameter.name] = _build_parameter(parameter, parameter.default)
        else:
            parameters_to_infer.append(parameter)

    for parameter in parameters_to_infer:
        param_cls: Type[Param] = Query

        if parameter.name in path_params and not any(
            isinstance(field, Path) and field.alias in path_params
            for field in parameters.values()
        ):
            param_cls = Path
        elif (isinstance(parameter.annotation, type) and issubclass(parameter.annotation, BaseModel)) or isinstance(
            parameter.default, BaseModel
        ):
            param_cls = Body

        param_spec: Param = param_cls(
            alias=parameter.name,
            default=parameter.default if parameter.default is not parameter.empty else Missing,
        )

        parameters[parameter.name] = _build_parameter(parameter, param_spec)

    actual_path_params: Set[str] = _extract_path_params(parameters.values())

    # Validate that only expected path params provided
    if path_params != actual_path_params:
        raise ValueError(
            f"Incompatible path params. Got: {actual_path_params}, expected: {path_params}"
        )

    return parameters


def build_request_specification(
    func: Callable, method: str, endpoint: str
) -> Specification:
    request: Request = Request(
        method=method,
        url=endpoint,
    )

    parameters: Dict[str, param.Parameter] = get_params(func, request=request)

    param_specs: Dict[str, Param] = {
        parameter.name: parameter.spec for parameter in parameters.values()
    }

    return Specification(
        request=request,
        params=param_specs,
    )
