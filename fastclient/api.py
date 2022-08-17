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
from arguments import Arguments
from typing_extensions import ParamSpec
from pydantic import BaseModel
from httpx import Response

from .sentinels import Missing
from .converters import (
    Converter,
    HttpxResolver,
    IdentityConverter,
    Resolver,
)
from .enums import Annotation, ParamType
from .models import Request, Specification
from .params import Body, Info, Param, Params, Path, Query
from . import utils

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
                if not isinstance(argument, Info):
                    continue

                if not argument.has_default():
                    raise ValueError(
                        f"{method.__name__}() missing argument: {argument_name!r}"
                    )

                arguments[argument_name] = argument.default

            destinations: Dict[ParamType, Dict[str, Any]] = {}

            parameter: str
            field: Info
            for parameter, field in specification.fields.items():
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


def build_request_specification(
    method: str, endpoint: str, signature: inspect.Signature
) -> Specification:
    if not signature.parameters:
        raise Exception("Method must have at least one parameter")

    parameters: List[Parameter] = list(signature.parameters.values())[1:]

    fields: Dict[str, Info] = {}
    fields_to_infer: List[inspect.Parameter] = []

    parameter: inspect.Parameter
    for parameter in parameters:
        default: Any = parameter.default

        if not isinstance(default, Info):
            fields_to_infer.append(parameter)

            continue

        field: Info = default

        if isinstance(field, Param) and field.alias is None:
            field.alias = field.generate_alias(parameter.name)

        fields[parameter.name] = field

    expected_path_params: Set[str] = utils.get_path_params(endpoint)

    param: inspect.Parameter
    for param in fields_to_infer:
        param_name: str = param.name
        param_default: Any = param.default
        param_annotation: type = param.annotation

        param_cls: Type[Param]

        if param_name in expected_path_params and not any(
            isinstance(field, Path) and field.alias in expected_path_params
            for field in fields.values()
        ):
            param_cls = Path
        elif issubclass(param_annotation, BaseModel) or isinstance(
            param_default, BaseModel
        ):
            param_cls = Body
        else:
            param_cls = Query

        fields[param_name] = param_cls(
            param_name,
            default=param_default if param_default is not parameter.empty else Missing,
        )

    actual_path_params: Set[str] = {
        field.alias
        for field in fields.values()
        if isinstance(field, Path) and field.alias is not None
    }

    # Validate that only expected path params provided
    if expected_path_params != actual_path_params:
        raise ValueError(
            f"Incompatible path params. Got: {actual_path_params}, expected: {expected_path_params}"
        )

    return Specification(
        method=method,
        url=endpoint,
        fields=fields,
    )
