"""OES shared utilities library."""

from .attrs import is_attrs_class, is_attrs_instance
from .cattrs import ExceptionDetails, get_exception_details
from .merge_dict import merge_dict
from .urlsafe_base64 import urlsafe_b64decode, urlsafe_b64encode

__all__ = [
    "merge_dict",
    "is_attrs_class",
    "is_attrs_instance",
    "ExceptionDetails",
    "get_exception_details",
    "urlsafe_b64encode",
    "urlsafe_b64decode",
    # modules
    "blacksheep",
    "logging",
]
