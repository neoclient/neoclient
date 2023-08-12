from typing import Any, Callable, Optional, TypeVar, overload

from .typing import Supplier

T = TypeVar("T")

@overload
def Query(
    name: Optional[str] = None,
    *,
    const: Optional[bool] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    regex: Optional[str] = None,
) -> Any: ...
@overload
def Query(
    name: Optional[str] = None,
    *,
    default: T,
    const: Optional[bool] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    regex: Optional[str] = None,
) -> Any: ...
@overload
def Query(
    name: Optional[str] = None,
    *,
    default_factory: Supplier[T],
    const: Optional[bool] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    regex: Optional[str] = None,
) -> T: ...
@overload
def Header(
    name: Optional[str] = None,
    *,
    const: Optional[bool] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    regex: Optional[str] = None,
    convert_underscores: bool = True,
) -> Any: ...
@overload
def Header(
    name: Optional[str] = None,
    *,
    default: T,
    const: Optional[bool] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    regex: Optional[str] = None,
    convert_underscores: bool = True,
) -> T: ...
@overload
def Header(
    name: Optional[str] = None,
    *,
    default_factory: Supplier[T],
    const: Optional[bool] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    regex: Optional[str] = None,
    convert_underscores: bool = True,
) -> T: ...
@overload
def Cookie(
    name: Optional[str] = None,
    *,
    const: Optional[bool] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    regex: Optional[str] = None,
) -> Any: ...
@overload
def Cookie(
    name: Optional[str] = None,
    *,
    default: T,
    const: Optional[bool] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    regex: Optional[str] = None,
) -> T: ...
@overload
def Cookie(
    name: Optional[str] = None,
    *,
    default_factory: Supplier[T],
    const: Optional[bool] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    regex: Optional[str] = None,
) -> T: ...
@overload
def Path(
    name: Optional[str] = None,
    *,
    const: Optional[bool] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    regex: Optional[str] = None,
) -> Any: ...
@overload
def Path(
    name: Optional[str] = None,
    *,
    default: T,
    const: Optional[bool] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    regex: Optional[str] = None,
) -> T: ...
@overload
def Path(
    name: Optional[str] = None,
    *,
    default_factory: Supplier[T],
    const: Optional[bool] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    regex: Optional[str] = None,
) -> T: ...

# Queries
@overload
def Queries(
    *,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    unique_items: Optional[bool] = None,
) -> Any: ...
@overload
def Queries(
    default: T,
    *,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    unique_items: Optional[bool] = None,
) -> T: ...
@overload
def Queries(
    *,
    default_factory: Supplier[T],
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    unique_items: Optional[bool] = None,
) -> T: ...

# Headers
@overload
def Headers(
    *,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    unique_items: Optional[bool] = None,
) -> Any: ...
@overload
def Headers(
    default: T,
    *,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    unique_items: Optional[bool] = None,
) -> T: ...
@overload
def Headers(
    *,
    default_factory: Supplier[T],
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    unique_items: Optional[bool] = None,
) -> T: ...

# Cookies
@overload
def Cookies(
    *,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    unique_items: Optional[bool] = None,
) -> Any: ...
@overload
def Cookies(
    default: T,
    *,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    unique_items: Optional[bool] = None,
) -> T: ...
@overload
def Cookies(
    *,
    default_factory: Supplier[T],
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    unique_items: Optional[bool] = None,
) -> T: ...

# Paths
@overload
def Paths(
    *,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    unique_items: Optional[bool] = None,
) -> Any: ...
@overload
def Paths(
    default: T,
    *,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    unique_items: Optional[bool] = None,
) -> T: ...
@overload
def Paths(
    *,
    default_factory: Supplier[T],
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    unique_items: Optional[bool] = None,
) -> T: ...

# Body
@overload
def Body(
    *,
    alias: Optional[str] = None,
    embed: bool = False,
) -> Any: ...
@overload
def Body(
    default: T,
    *,
    alias: Optional[str] = None,
    embed: bool = False,
) -> T: ...
@overload
def Body(
    *,
    default_factory: Callable[[], T],
    alias: Optional[str] = None,
    embed: bool = False,
) -> T: ...

# Depends
@overload
def Depends(*, use_cache: bool = True) -> Any: ...
@overload
def Depends(dependency: Callable[..., T], /, *, use_cache: bool = True) -> T: ...

# URL
def URL() -> Any: ...

# Request
def Request() -> Any: ...

# Response
def Response() -> Any: ...

# StatusCode
def StatusCode() -> Any: ...

# Reason
def Reason() -> Any: ...

# State
@overload
def State(name: Optional[str] = None) -> Any: ...
@overload
def State(name: Optional[str] = None, *, default: T) -> Any: ...
@overload
def State(name: Optional[str] = None, *, default_factory: Supplier[T]) -> T: ...
