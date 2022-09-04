from typing import Literal, Type
from sentinel import Sentinel

class Foo(Sentinel): pass

x: Type[Foo] = Foo