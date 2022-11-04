from typing import (
    Any,
    Callable,
    Optional,
    TypeVar,
    overload,
)

T = TypeVar("T")

# Query
@overload
def Query(alias: Optional[str] = None, *, required: bool = False) -> Any: ...
@overload
def Query(alias: Optional[str] = None, *, default: T, required: bool = False) -> T: ...
@overload
def Query(
    alias: Optional[str] = None,
    *,
    default_factory: Callable[[], T],
    required: bool = False,
) -> T: ...

# Header
@overload
def Header(alias: Optional[str] = None, *, required: bool = False) -> Any: ...
@overload
def Header(alias: Optional[str] = None, *, default: T, required: bool = False) -> T: ...
@overload
def Header(
    alias: Optional[str] = None,
    *,
    default_factory: Callable[[], T],
    required: bool = False,
) -> T: ...

# Cookie
@overload
def Cookie(alias: Optional[str] = None, *, required: bool = False) -> Any: ...
@overload
def Cookie(alias: Optional[str] = None, *, default: T, required: bool = False) -> T: ...
@overload
def Cookie(
    alias: Optional[str] = None,
    *,
    default_factory: Callable[[], T],
    required: bool = False,
) -> T: ...

# Path
@overload
def Path(alias: Optional[str] = None, *, required: bool = False) -> Any: ...
@overload
def Path(alias: Optional[str] = None, *, default: T, required: bool = False) -> T: ...
@overload
def Path(
    alias: Optional[str] = None,
    *,
    default_factory: Callable[[], T],
    required: bool = False,
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
