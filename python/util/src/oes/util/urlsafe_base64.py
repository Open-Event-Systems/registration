"""URL safe base64 encoding."""
import base64
from typing import Union


def urlsafe_b64encode(data: Union[bytes, bytearray, memoryview]) -> str:
    """URL-safe base64 encode the data, stripping padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def urlsafe_b64decode(data: str) -> bytes:
    """URL-safe base64 decode the string without throwing padding errors."""
    return base64.urlsafe_b64decode(data + "==")
