import inspect
from inspect import Parameter
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
)

import annotate
import httpx
import param
import parse
import pydantic
from arguments import Arguments
from httpx import Response
from param import ParameterType
from param.sentinels import Missing
from pydantic import BaseModel
from typing_extensions import ParamSpec

from . import utils
from .enums import Annotation, ParamType
from .models import RequestOptions, OperationSpecification
from .params import Body, Depends, Param, Params, Path, Promise, Query
from .operations import Operation

T = TypeVar("T")

PT = ParamSpec("PT")
RT = TypeVar("RT")


def get_specification(obj: Any, /) -> Optional[OperationSpecification]:
    return annotate.get_annotations(obj).get(Annotation.SPECIFICATION)


def has_specification(obj: Any, /) -> bool:
    return Annotation.SPECIFICATION in annotate.get_annotations(obj)


def get_operations(cls: type, /) -> List[Operation]:
    return [
        member
        for _, member in inspect.getmembers(cls)
        if isinstance(member, Operation)
    ]


def get_response_arguments(
    response: Response,
    parameters: Dict[str, param.Parameter],
    request: RequestOptions,
    /,
    *,
    cached_dependencies: Optional[Dict[Callable[..., Any], Any]] = None,
) -> Arguments:
    args: List[Any] = []
    kwargs: Dict[str, Any] = {}

    if cached_dependencies is None:
        cached_dependencies = {}

    parameter: param.Parameter
    for parameter in parameters.values():
        value: Any = None

        if isinstance(parameter.spec, Params):
            if parameter.spec.type is ParamType.QUERY:
                value = dict(response.request.url.params)
            elif parameter.spec.type is ParamType.HEADER:
                if parameter.annotation in (inspect._empty, Missing, httpx.Headers):
                    value = response.headers
                elif parameter.annotation is dict:
                    value = dict(response.headers)
                else:
                    raise Exception(f"Headers dependency has incompatible annotation: {parameter.annotation!r}")
            elif parameter.spec.type is ParamType.COOKIE:
                if parameter.annotation in (inspect._empty, Missing, httpx.Cookies):
                    value = response.cookies
                elif parameter.annotation is dict:
                    value = dict(response.cookies)
                else:
                    raise Exception(f"Cookies dependency has incompatible annotation: {parameter.annotation!r}")
            else:
                raise Exception(f"Unknown multi-param of type {parameter.spec.type}")
        elif isinstance(parameter.spec, Param):
            parameter_alias: str = (
                parameter.spec.alias
                if parameter.spec.alias is not None
                else parameter.spec.generate_alias(parameter.name)
            )

            if parameter.spec.type is ParamType.QUERY:
                value = response.request.url.params[parameter_alias]
            elif parameter.spec.type is ParamType.HEADER:
                value = response.headers[parameter_alias]
            elif parameter.spec.type is ParamType.PATH:
                parse_result: Optional[parse.Result] = parse.parse(
                    request.url, response.request.url.path
                )

                if parse_result is None:
                    raise Exception(
                        f"Failed to parse uri {response.request.url.path!r} against format spec {request.url!r}"
                    )

                value = parse_result.named[parameter_alias]
            elif parameter.spec.type is ParamType.COOKIE:
                value = response.cookies[parameter_alias]
            elif parameter.spec.type is ParamType.BODY:
                if parameter.annotation is not inspect._empty:
                    value = pydantic.parse_raw_as(parameter.annotation, response.text)
                else:
                    value = response.json()
            else:
                raise Exception(f"Unknown ParamType: {parameter.spec.type}")
        elif isinstance(parameter.spec, Depends):
            if (
                cached_dependencies is not None
                and parameter.spec.use_cache
                and parameter.spec.dependency in cached_dependencies
            ):
                value = cached_dependencies[parameter.spec.dependency]
            else:
                if parameter.spec.dependency is None:
                    raise Exception(
                        "TODO: Support dependencies with no explicit dependency"
                    )
                else:
                    sub_parameters: Dict[str, param.Parameter] = get_params(
                        parameter.spec.dependency, request=request
                    )
                    sub_arguments: Arguments = get_response_arguments(
                        response,
                        sub_parameters,
                        request,
                        cached_dependencies=cached_dependencies,
                    )

                    value = sub_arguments.call(parameter.spec.dependency)

                cached_dependencies[parameter.spec.dependency] = value
        elif isinstance(parameter.spec, Promise):
            promised_type: type

            if parameter.spec.promised_type is not None:
                promised_type = parameter.spec.promised_type
            elif parameter.annotation is not inspect._empty:
                promised_type = parameter.annotation
            else:
                raise Exception("Cannot promise no type!")

            # TODO: Support more promised types
            if promised_type is httpx.Response:
                value = response
            elif promised_type is httpx.Request:
                value = request
            else:
                raise Exception(
                    f"Unsupported promised type: {parameter.spec.promised_type!r}"
                )
        else:
            raise Exception(f"Unknown parameter spec class: {type(parameter.spec)}")

        if parameter.type in (
            ParameterType.POSITIONAL_ONLY,
            ParameterType.VAR_POSITIONAL,
        ):
            args.append(value)
        else:
            kwargs[parameter.name] = value

    return Arguments(*args, **kwargs)


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
    func: Callable, /, *, request: Optional[RequestOptions] = None
) -> Dict[str, param.Parameter]:
    path_params: Set[str] = (
        utils.get_path_params(str(request.url)) if request is not None else set()
    )

    _inspect_params: List[Parameter] = list(inspect.signature(func).parameters.values())

    raw_parameters = _inspect_params

    parameters: Dict[str, param.Parameter] = {}
    parameters_to_infer: List[Parameter] = []

    parameter: Parameter

    for parameter in raw_parameters:
        # NOTE: `Depends` doesn't subclass `Param`. This needs to be fixed.
        # "responses" (e.g. `responses.status_code`) also don't subclass `Param`...
        if isinstance(parameter.default, (Param, Depends, Promise)):
            parameters[parameter.name] = _build_parameter(parameter, parameter.default)
        else:
            parameters_to_infer.append(parameter)

    for parameter in parameters_to_infer:
        param_cls: Type[Param] = Query

        parameter_type: type = parameter.annotation

        body_types: Tuple[type, ...] = (BaseModel, dict)

        if parameter.name in path_params and not any(
            isinstance(field, Path) and field.alias in path_params
            for field in parameters.values()
        ):
            param_cls = Path
        elif (
            parameter.annotation is not parameter.empty
            and isinstance(parameter_type, type)
            and any(issubclass(parameter_type, body_type) for body_type in body_types)
        ):
            param_cls = Body

        param_spec: Param = param_cls(
            alias=parameter.name,
            default=parameter.default
            if parameter.default is not parameter.empty
            else Missing,
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
    func: Callable,
    method: str,
    endpoint: str,
    *,
    response: Optional[Callable[..., Any]] = None,
) -> OperationSpecification:
    request: RequestOptions = RequestOptions(
        method=method,
        url=endpoint,
    )

    parameters: Dict[str, param.Parameter] = get_params(func, request=request)

    param_specs: Dict[str, Param] = {
        parameter.name: parameter.spec for parameter in parameters.values()
    }

    return OperationSpecification(
        request=request,
        response=response,
        params=param_specs,
    )
