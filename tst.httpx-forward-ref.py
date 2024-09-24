from typing import get_type_hints

from httpx import Request

th = get_type_hints(Request.__init__)
