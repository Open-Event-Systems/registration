"""Access token."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

import jwt
from attrs import frozen
from cattrs import BaseValidationError
from cattrs.gen import make_dict_unstructure_fn
from cattrs.preconf.orjson import make_converter
from typing_extensions import Self

converter = make_converter()


class TokenError(ValueError):
    """Raised when a token is invalid."""

    pass


@frozen
class TokenBase:
    """Base token class."""

    iss: Literal["oes"]
    exp: datetime

    def encode(self, *, key: str) -> str:
        """Encode the JWT."""
        as_dict = converter.unstructure(self)
        return jwt.encode(as_dict, key=key, algorithm="HS256")

    @classmethod
    def decode(cls, data: str, *, key: str) -> Self:
        """Decode the JWT."""
        try:
            data = jwt.decode(data, key=key, algorithms=["HS256"], issuer="oes")
        except jwt.InvalidTokenError as exc:
            raise TokenError("Token is invalid") from exc

        try:
            structured = converter.structure(data, cls)
        except BaseValidationError as exc:
            raise TokenError("Token parsing failed") from exc

        return structured


@frozen
class AccessToken(TokenBase):
    """Access token."""

    typ: Literal["at"]
    sub: str | None = None


converter.register_structure_hook(
    datetime, lambda v, t: datetime.fromtimestamp(v).astimezone()
)
converter.register_unstructure_hook(datetime, lambda d: int(d.timestamp()))

converter.register_unstructure_hook_factory(
    lambda cls: isinstance(cls, type) and issubclass(cls, TokenBase),
    lambda cls: make_dict_unstructure_fn(cls, converter, _cattrs_omit_if_default=True),
)
