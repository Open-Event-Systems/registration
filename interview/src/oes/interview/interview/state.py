"""State module."""
from __future__ import annotations

import uuid
import zlib
from collections.abc import Callable, Mapping, Set
from datetime import datetime, timedelta, timezone
from struct import Struct
from typing import Any, Optional, Union, overload

import orjson
from attrs import Factory, evolve, field, frozen
from cattrs import Converter, override
from cattrs.gen import make_dict_structure_fn, make_dict_unstructure_fn
from nacl.secret import SecretBox
from oes.interview.interview.error import InvalidStateError
from oes.interview.interview.interview import Interview
from oes.interview.variables.locator import Locator
from oes.template import Context
from oes.util import merge_dict
from typing_extensions import Self

DEFAULT_INTERVIEW_EXPIRATION = timedelta(seconds=1800)
"""The default amount of time an interview state is valid."""


def _default_exp() -> datetime:
    now = datetime.now().astimezone()
    return now + DEFAULT_INTERVIEW_EXPIRATION


@frozen(kw_only=True)
class InterviewState:
    """An interview state."""

    interview: Interview = Interview()
    """The interview."""

    target_url: Optional[str] = None
    """The target URL."""

    submission_id: str = Factory(lambda: uuid.uuid4().hex)
    """Unique ID for this submission."""

    expiration_date: datetime = field(
        factory=_default_exp, converter=lambda v: v if v is not None else _default_exp()
    )
    """When the interview expires."""

    complete: bool = False
    """Whether the state is complete."""

    context: Context = field(
        converter=lambda v: merge_dict({}, v),
        factory=dict,
    )
    """Context data."""

    answered_question_ids: Set[str] = frozenset()
    """Answered question IDs."""

    question_id: Optional[str] = None
    """The current question ID."""

    data: Context = field(
        converter=lambda v: merge_dict({}, v),
        factory=dict,
    )
    """Interview data."""

    _template_context: Context = field(
        default=Factory(lambda s: merge_dict(s.data, s.context), takes_self=True),
        init=False,
        eq=False,
    )

    @property
    def template_context(self) -> Context:
        """The context to use when evaluating templates."""
        return dict(self._template_context)

    def set_question(self, question_id: Optional[str]) -> Self:
        """Set or clear the current question ID.

        Updates :attr:`question_id` and :attr:`answered_question_ids`.
        """
        if question_id is not None:
            return evolve(
                self,
                question_id=question_id,
                answered_question_ids=self.answered_question_ids | {question_id},
            )
        else:
            return evolve(
                self,
                question_id=None,
            )

    def set_data(self, data: Context) -> Self:
        """Replace the :attr:`data` attribute."""
        return evolve(
            self,
            data=data,
        )

    @overload
    def set_values(self, __values: Mapping[Locator, object]) -> Self:
        ...

    @overload
    def set_values(self, __loc: Locator, __value: object) -> Self:
        ...

    def set_values(
        self, val_or_loc: Union[Locator, Mapping[Locator, object]], *vals: object
    ) -> Self:
        """Set values in the :attr:`data` and return the new state.

        Accepts either a mapping of :class:`Locator` to objects, or a single
        :class:`Locator` and a value.
        """

        if isinstance(val_or_loc, Mapping) and len(vals) == 0:
            to_set = val_or_loc
        else:
            to_set = {val_or_loc: vals[0]}

        new_data = merge_dict({}, self.data)
        for loc, val in to_set.items():
            loc.set(val, new_data)

        return evolve(
            self,
            data=new_data,
        )

    def set_complete(self) -> Self:
        """Mark complete."""
        return evolve(
            self,
            complete=True,
        )

    def encrypt(
        self,
        *,
        secret: bytes,
        converter: Converter,
        default: Optional[Callable[[Any], Any]] = None,
    ) -> bytes:
        """Encrypt this state.

        Args:
            secret: The key.
            converter: The converter.
            default: A JSON ``default`` function.
        """
        as_bytes = _encode_state(self, converter, default=default)

        box = SecretBox(secret)
        return box.encrypt(as_bytes)

    @classmethod
    def decrypt(
        cls, encrypted: bytes, *, converter: Converter, secret: bytes
    ) -> InterviewState:
        """Decrypt an encrypted state.

        Warning:
            Does not check the expiration date or perform other validation.

        Args:
            encrypted: The encrypted state.
            converter: The converter.
            secret: The key.

        Returns:
            The decrypted :class:`InterviewState`.

        Raises:
            InvalidStateError: If decryption/verification fails.
        """

        try:
            box = SecretBox(secret)
            decrypted = box.decrypt(encrypted)
            view = memoryview(decrypted)
            parsed = _decode_state(view, converter)
        except Exception as e:
            raise InvalidStateError("Interview state is not valid") from e

        return parsed

    def get_is_expired(self, *, now: Optional[datetime] = None) -> bool:
        """Return whether the state is expired."""
        now = now if now is not None else datetime.now(tz=timezone.utc)
        return now >= self.expiration_date

    def validate(self, *, now: Optional[datetime] = None):
        """Check that the state is valid.

        Args:
            now: The current ``datetime``.

        Raises:
            InvalidStateError: If the state is expired.
        """
        if self.get_is_expired(now=now):
            raise InvalidStateError("Interview state is expired")


def make_interview_state_structure_fn(
    converter: Converter,
) -> Callable[[Mapping[str, Any], Any], InterviewState]:
    """Get a function to structure an :class:`InterviewState`."""

    return make_dict_structure_fn(
        InterviewState,
        converter,
        _template_context=override(omit=True),
    )


def make_interview_state_unstructure_fn(
    converter: Converter,
) -> Callable[[InterviewState], Mapping[str, Any]]:
    """Get a function to unstructure an :class:`InterviewState`."""

    return make_dict_unstructure_fn(
        InterviewState,
        converter,
        _template_context=override(omit=True),
    )


_ver = Struct("B")
_data = Struct("<i")


def _encode_state(
    state: InterviewState,
    converter: Converter,
    default: Optional[Callable[[Any], Any]] = None,
) -> bytes:
    as_dict: dict[str, Any] = converter.unstructure(state)
    data = as_dict.pop("data")
    return (
        _ver.pack(1)
        + _encode_data(as_dict, compress=True, default=default)
        + _encode_data({"data": data}, compress=False, default=default)
    )


def _decode_state(data: memoryview, converter: Converter) -> InterviewState:
    (ver,) = _ver.unpack_from(data)
    if ver != 1:
        raise ValueError("Invalid data")

    i = _ver.size

    as_dict: dict[str, Any] = {}

    while i < len(data):
        ct, part = _decode_data(data[i:])
        as_dict.update(part)
        i += ct

    return converter.structure(as_dict, InterviewState)


def _encode_data(
    data: Mapping[str, Any],
    compress: bool = False,
    default: Optional[Callable[[Any], Any]] = None,
) -> bytes:
    json_bytes = orjson.dumps(data, default=default)

    if compress:
        compressed = zlib.compress(json_bytes)
        result = _data.pack(-len(compressed)) + compressed
    else:
        result = _data.pack(len(json_bytes)) + json_bytes

    return result


def _decode_data(data: memoryview) -> tuple[int, Mapping[str, Any]]:
    (size,) = _data.unpack_from(data)

    if size < 0:
        size = -size
        compressed = True
    else:
        compressed = False

    if len(data) < _data.size + size:
        raise ValueError("Invalid data")

    body = data[_data.size : _data.size + size]

    if compressed:
        decompressed = zlib.decompress(body)
        return _data.size + size, orjson.loads(decompressed)
    else:
        return _data.size + size, orjson.loads(body)
