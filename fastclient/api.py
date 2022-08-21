import functools
import inspect
from dataclasses import dataclass
from inspect import Parameter, Signature
from types import FunctionType
from typing import (
    Any,
    Callable,
    Dict,
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
from arguments import Arguments
from httpx import Response
from param import Missing
from pydantic import BaseModel
from typing_extensions import ParamSpec

from . import utils
from .converters import Converter, HttpxResolver, IdentityConverter, Resolver
from .enums import Annotation, ParamType
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
            ) and not furl.has_netloc(specification.url):
                raise Exception(
                    f"Cannot construct fully-qualified URL from: base_url={self.base_url!r}, endpoint={specification.url!r}"
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
            for parameter, field in specification.param_specs.items():
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

                    if field.type is ParamType.BODY and not isinstance(
                        value, BaseModel
                    ):
                        raise Exception(
                            "Can only currently accept pydantic request bodies"
                        )

                    destinations.setdefault(field.type, {})[field_name] = value
                elif isinstance(field, Params):
                    destinations.setdefault(field.type, {}).update(value)
                else:
                    raise Exception(f"Unknown field type: {field}")

            body_params: Dict[str, Any] = destinations.get(ParamType.BODY, {})

            json: Optional[dict] = None

            # If there's only onw body param, make it the entire JSON request body
            if len(body_params) == 1:
                json = list(body_params.values())[0].dict()
            # If there are multiple body params, construct a multi-level dict
            # of each body parameter. E.g. (user: User, item: Item) -> {"user": ..., "item": ...}
            elif body_params:
                json = {key: val.dict() for key, val in body_params.items()}

            request: Request = Request(
                method=specification.method,
                url=self._url(specification.url).format(
                    **destinations.get(ParamType.PATH, {})
                ),
                params={
                    **specification.params,
                    **destinations.get(ParamType.QUERY, {}),
                },
                headers={
                    **specification.headers,
                    **destinations.get(ParamType.HEADER, {}),
                },
                cookies={
                    **specification.cookies,
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
            if issubclass(return_annotation, BaseModel):
                return return_annotation.parse_obj(response.json())
            if return_annotation is str:
                return response.text
            if return_annotation is bytes:
                return response.content
            if return_annotation is int:
                return int(response.text)
            if return_annotation is float:
                return float(response.text)
            if return_annotation is dict:
                return response.json()
            if return_annotation is list:
                return response.json()
            if return_annotation is tuple:
                return response.json()
            if return_annotation is set:
                return response.json()
            if return_annotation is bool:
                return response.text == "True"

            raise Exception(
                f"Unknown return annotation {return_annotation!r}, cannot convert response"
            )

        return wrapper


def get_params(func: Callable, /, path_params: Set[str]) -> Dict[str, param.Parameter]:
    raw_parameters: List[Parameter] = list(inspect.signature(func).parameters.values())[
        1:
    ]

    parameters: Dict[str, parameter.Parameter] = {}
    parameters_to_infer: List[Parameter] = []

    parameter: Parameter
    for parameter in raw_parameters:
        if not isinstance(parameter.default, Param):
            parameters_to_infer.append(parameter)

            continue

        parameters[parameter.name] = param.Parameter(
            name=parameter.name,
            annotation=parameter.annotation,
            type=getattr(param.ParameterType, parameter.kind.name),
            spec=parameter.default,
        )

    for parameter in parameters_to_infer:
        param_default: Any = parameter.default
        param_annotation: type = parameter.annotation

        param_cls: Type[Param]

        if parameter.name in path_params and not any(
            isinstance(field, Path) and field.alias in path_params
            for field in parameters.values()
        ):
            param_cls = Path
        elif issubclass(param_annotation, BaseModel) or isinstance(
            param_default, BaseModel
        ):
            param_cls = Body
        else:
            param_cls = Query

        param_spec: Param = param_cls(
            alias=parameter.name,
            default=param_default if param_default is not parameter.empty else Missing,
        )

        parameters[parameter.name] = param.Parameter(
            name=parameter.name,
            annotation=parameter.annotation,
            type=getattr(param.ParameterType, parameter.kind.name),
            spec=param_spec,
        )

    actual_path_params: Set[str] = {
        (
            parameter.spec.alias
            if parameter.spec.alias is not None
            else parameter.spec.generate_alias(parameter.name)
        )
        for parameter in parameters.values()
        if isinstance(parameter.spec, Path)
    }

    # Validate that only expected path params provided
    if path_params != actual_path_params:
        raise ValueError(
            f"Incompatible path params. Got: {actual_path_params}, expected: {path_params}"
        )

    return parameters


def build_request_specification(
    func: Callable, method: str, endpoint: str
) -> Specification:
    expected_path_params: Set[str] = utils.get_path_params(endpoint)
    parameters: Dict[str, param.Parameter] = get_params(func, expected_path_params)

    param_specs: Dict[str, Param] = {
        parameter.name: parameter.spec for parameter in parameters.values()
    }

    return Specification(
        method=method,
        url=endpoint,
        param_specs=param_specs,
    )
