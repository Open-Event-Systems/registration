"""Request parsing methods."""
import base64
from typing import Any, Mapping, Optional

import orjson
from attrs import field, frozen, validators
from blacksheep import Request
from blacksheep.exceptions import BadRequest
from cattrs import BaseValidationError
from cattrs.preconf.orjson import make_converter
from loguru import logger
from oes.interview.interview.error import InvalidStateError
from oes.interview.interview.state import InterviewState
from oes.interview.serialization import converter
from oes.interview.server.settings import Settings


@frozen(kw_only=True)
class UpdateRequest:
    """An update request body."""

    state: bytes
    responses: Optional[dict[str, Any]] = None


def _from_b85(v: object) -> bytes:
    if isinstance(v, bytes):
        return v
    elif isinstance(v, str):
        return base64.b85decode(v)
    else:
        raise TypeError(f"Invalid bytes {v}")


def _load_json(v: object) -> object:
    if isinstance(v, bytes):
        return orjson.loads(v)
    else:
        return v


@frozen(kw_only=True)
class JSONRequest(UpdateRequest):
    state: bytes = field(converter=_from_b85)
    responses: Optional[dict[str, Any]] = field(
        default=None,
        validator=validators.optional(
            [
                validators.deep_mapping(
                    key_validator=validators.instance_of(str),
                    value_validator=validators.instance_of(object),
                    mapping_validator=validators.instance_of(dict),
                )
            ]
        ),
    )


@frozen(kw_only=True)
class MultipartRequest(UpdateRequest):
    responses: Optional[dict[str, Any]] = field(
        default=None,
        converter=_load_json,
        validator=validators.optional(
            [
                validators.deep_mapping(
                    key_validator=validators.instance_of(str),
                    value_validator=validators.instance_of(object),
                    mapping_validator=validators.instance_of(dict),
                )
            ]
        ),
    )


request_converter = make_converter(
    prefer_attrib_converters=True, detailed_validation=False
)

request_converter.register_structure_hook(
    bytes, lambda v, _: v if isinstance(v, bytes) else base64.b85decode(v)
)


async def parse_request(request: Request) -> UpdateRequest:
    """Parse a request body."""
    if request.declares_content_type(b"application/json"):
        return await _parse_json_request(request)
    elif request.declares_content_type(b"multipart/form-data"):
        return await _parse_multipart_request(request)
    else:
        raise BadRequest


def validate_state(state: bytes, settings: Settings) -> InterviewState:
    """Validate the interview state."""
    assert settings.encryption_key is not None

    try:
        decrypted = InterviewState.decrypt(
            state,
            converter=converter,
            secret=settings.encryption_key.get_secret_value(),
        )
        decrypted.validate()
        return decrypted
    except InvalidStateError as e:
        logger.debug(f"Invalid state: {e}")
        raise BadRequest


async def _parse_json_request(request: Request) -> JSONRequest:
    """Parse a normal JSON request."""
    body = await _read_request(request)
    try:
        data = request_converter.loads(body, JSONRequest)
        return data
    except (ValueError, BaseValidationError):
        raise BadRequest


async def _parse_multipart_request(request: Request) -> MultipartRequest:
    """Parse a ``multipart/form-data`` request."""

    parts = dict(await _get_multipart(request))
    if "state" in parts:
        parts["state"] = _strip_state(parts["state"])

    return request_converter.structure(parts, MultipartRequest)


async def _get_multipart(request: Request) -> Mapping[str, bytes]:
    parts = {}
    multipart_parts = await request.multipart()
    for part in multipart_parts or []:
        if part.name in parts or part.name not in (b"state", b"responses"):
            raise BadRequest
        parts[part.name] = part.data

    return {n.decode(): d for n, d in parts.items()}


def _strip_state(s: bytes) -> bytes:
    _, _, res = s.partition(b"\r\n\r\n")
    return res


async def _read_request(request: Request) -> bytes:
    body = await request.read()
    if not body:
        raise BadRequest

    return body
