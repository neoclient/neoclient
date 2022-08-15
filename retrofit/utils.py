from inspect import Parameter, Signature
from typing import Any, Dict, List


def get_arguments(args: Any, kwargs: Any, signature: Signature) -> Dict[str, Any]:
    positional_parameters: List[Parameter] = list(signature.parameters.values())[
        : len(args)
    ]

    positional: Dict[str, Any] = {
        parameter.name: arg for arg, parameter in zip(args, positional_parameters)
    }

    defaults: Dict[str, Any] = {
        parameter.name: parameter.default
        for parameter in signature.parameters.values()
        if parameter.default is not parameter.empty
    }

    return {**defaults, **positional, **kwargs}
