"""Docs helpers."""
from collections.abc import Callable, Mapping
from typing import Any, Optional, TypeVar, Union

from blacksheep.server.openapi.common import (
    ContentInfo,
    ParameterInfo,
    RequestBodyInfo,
    ResponseInfo,
    ResponseStatusType,
)
from blacksheep.server.openapi.v3 import OpenAPIHandler
from typing_extensions import ParamSpec

_P = ParamSpec("_P")
_R = TypeVar("_R")


class DocsHelper:
    """Docs helper decorator."""

    def __init__(self, docs: OpenAPIHandler):
        self._docs = docs

    def __call__(
        self,
        *,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[list[str]] = None,
        status_code: Optional[int] = None,
        response_type: Optional[type] = None,
        response_summary: Optional[str] = None,
        parameters: Optional[Mapping[str, ParameterInfo]] = None,
        request_body: Optional[RequestBodyInfo] = None,
        responses: Optional[dict[ResponseStatusType, Union[str, ResponseInfo]]] = None,
        ignored: Optional[bool] = None,
        deprecated: Optional[bool] = None,
        on_created: Optional[Callable[[Any, Any], None]] = None,
    ) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
        if response_type is not None:
            responses = dict(responses or {})
            responses[status_code or 200] = ResponseInfo(
                response_summary or "",
                content=[
                    ContentInfo(
                        type=response_type,
                    ),
                ],
            )

        return self._docs(
            summary=summary,
            description=description,
            tags=tags,
            parameters=parameters,
            request_body=request_body,
            responses=responses,
            ignored=ignored,
            deprecated=deprecated,
            on_created=on_created,
        )
