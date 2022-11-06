from typing import Any, Callable, Optional, TypeVar, overload

from .typing import Supplier

T = TypeVar("T")

# TODO TODO TODO
# NOTE: These all need to be updated to support the extra parameters the `parameter_functions` now have
# `Query` has been done as an example
# TODO TODO TODO

# Query
@overload
def Query(
    alias: Optional[str] = ...,
    const: Optional[bool] = ...,
    gt: Optional[float] = ...,
    ge: Optional[float] = ...,
    lt: Optional[float] = ...,
    le: Optional[float] = ...,
    multiple_of: Optional[float] = ...,
    allow_inf_nan: Optional[bool] = ...,
    max_digits: Optional[int] = ...,
    decimal_places: Optional[int] = ...,
    min_length: Optional[int] = ...,
    max_length: Optional[int] = ...,
    regex: Optional[str] = ...,
) -> Any: ...
@overload
def Query(
    default: T,
    *,
    alias: Optional[str] = ...,
    const: Optional[bool] = ...,
    gt: Optional[float] = ...,
    ge: Optional[float] = ...,
    lt: Optional[float] = ...,
    le: Optional[float] = ...,
    multiple_of: Optional[float] = ...,
    allow_inf_nan: Optional[bool] = ...,
    max_digits: Optional[int] = ...,
    decimal_places: Optional[int] = ...,
    min_length: Optional[int] = ...,
    max_length: Optional[int] = ...,
    regex: Optional[str] = ...,
) -> T: ...
@overload
def Query(
    *,
    default_factory: Supplier[T],
    alias: Optional[str] = ...,
    const: Optional[bool] = ...,
    gt: Optional[float] = ...,
    ge: Optional[float] = ...,
    lt: Optional[float] = ...,
    le: Optional[float] = ...,
    multiple_of: Optional[float] = ...,
    allow_inf_nan: Optional[bool] = ...,
    max_digits: Optional[int] = ...,
    decimal_places: Optional[int] = ...,
    min_length: Optional[int] = ...,
    max_length: Optional[int] = ...,
    regex: Optional[str] = ...,
) -> T: ...

# Header
@overload
def Header(alias: Optional[str] = None) -> Any: ...
@overload
def Header(alias: Optional[str] = None, *, default: T) -> T: ...
@overload
def Header(
    alias: Optional[str] = None,
    *,
    default_factory: Callable[[], T],
) -> T: ...

# Cookie
@overload
def Cookie(alias: Optional[str] = None) -> Any: ...
@overload
def Cookie(alias: Optional[str] = None, *, default: T) -> T: ...
@overload
def Cookie(
    alias: Optional[str] = None,
    *,
    default_factory: Callable[[], T],
) -> T: ...

# Path
@overload
def Path(alias: Optional[str] = None) -> Any: ...
@overload
def Path(alias: Optional[str] = None, *, default: T) -> T: ...
@overload
def Path(
    alias: Optional[str] = None,
    *,
    default_factory: Callable[[], T],
) -> T: ...

# Queries
@overload
def Queries() -> Any: ...
@overload
def Queries(*, default: T) -> T: ...
@overload
def Queries(*, default_factory: Callable[[], T]) -> T: ...

# Headers
@overload
def Headers() -> Any: ...
@overload
def Headers(*, default: T) -> T: ...
@overload
def Headers(*, default_factory: Callable[[], T]) -> T: ...

# Cookies
@overload
def Cookies() -> Any: ...
@overload
def Cookies(*, default: T) -> T: ...
@overload
def Cookies(*, default_factory: Callable[[], T]) -> T: ...

# Paths
@overload
def Paths() -> Any: ...
@overload
def Paths(*, default: T) -> T: ...
@overload
def Paths(*, default_factory: Callable[[], T]) -> T: ...

# Body
@overload
def Body(
    alias: Optional[str] = None, *, required: bool = False, embed: bool = False
) -> Any: ...
@overload
def Body(
    alias: Optional[str] = None,
    *,
    default: T,
    required: bool = False,
    embed: bool = False,
) -> T: ...
@overload
def Body(
    alias: Optional[str] = None,
    *,
    default_factory: Callable[[], T],
    required: bool = False,
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
