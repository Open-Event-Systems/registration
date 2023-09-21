import os
from datetime import datetime, timezone

import pytest
from oes.interview.interview.error import InvalidStateError
from oes.interview.interview.state import InterviewState
from oes.interview.serialization import converter
from oes.interview.variables.locator import parse_locator


def test_template_context():
    state = InterviewState(context={"a": 1}, data={"a": 2, "b": 3})
    assert state.template_context == {"a": 1, "b": 3}


def test_set_question():
    state = InterviewState()
    state = state.set_question("q1")
    assert state.question_id == "q1"
    assert state.answered_question_ids == {"q1"}
    state = state.set_question(None)
    assert state.question_id is None
    assert state.answered_question_ids == {"q1"}


def test_set_data_is_not_mutable_and_preserves_context():
    init_context = {"ctx": {"a": 1}}
    init_data = {"a": {"b": 1}, "c": 2}
    state = InterviewState(context=init_context, data=init_data)

    init_context["ctx"]["a"] = 2
    init_data["a"]["x"] = 1
    init_data["d"] = 3

    assert state.context == {"ctx": {"a": 1}}
    assert state.data == {"a": {"b": 1}, "c": 2}
    assert state.template_context == {"a": {"b": 1}, "c": 2, "ctx": {"a": 1}}

    new_data = {"a": {"b": 2}, "c": 3, "ctx": "overwritten?"}
    state = state.set_data(new_data)
    new_data["a"]["x"] = True

    assert state.context == {"ctx": {"a": 1}}
    assert state.data == {"a": {"b": 2}, "c": 3, "ctx": "overwritten?"}
    assert state.template_context == {"a": {"b": 2}, "c": 3, "ctx": {"a": 1}}

    state = state.set_data({})
    assert state.data == {}
    assert state.context == {"ctx": {"a": 1}}
    assert state.template_context == {"ctx": {"a": 1}}


def test_set_complete():
    state = InterviewState()
    assert not state.complete
    state = state.set_complete()
    assert state.complete


def test_set_values():
    state = InterviewState(
        context={"ctx": {"a": 1}},
        data={"a": {"b": 1}, "c": 2},
    )

    values = {
        parse_locator("c"): 3,
        parse_locator("a.b"): 2,
    }

    state = state.set_values(values)
    assert state.data == {"a": {"b": 2}, "c": 3}

    state = state.set_values(parse_locator("a.d"), 4)
    assert state.data == {"a": {"b": 2, "d": 4}, "c": 3}


def test_encrypt_decrypt():
    state = InterviewState(
        target_url="http://localhost",
        submission_id="s1",
        expiration_date=datetime(2020, 1, 1, tzinfo=timezone.utc),
        context={
            "test": True,
        },
        data={
            "test2": 2,
        },
    )

    key = os.urandom(32)

    enc = state.encrypt(secret=key, converter=converter)
    assert isinstance(enc, bytes)

    dec = state.decrypt(enc, secret=key, converter=converter)
    assert dec == state


def test_encrypt_decrypt_invalid_key():
    state = InterviewState(
        target_url="http://localhost",
        submission_id="s1",
        expiration_date=datetime(2020, 1, 1, tzinfo=timezone.utc),
        context={
            "test": True,
        },
        data={
            "test2": 2,
        },
    )

    key = os.urandom(32)

    enc = state.encrypt(secret=key, converter=converter)

    key2 = bytearray(key)
    key2[16] = (key[16] + 1) % 256

    with pytest.raises(InvalidStateError):
        state.decrypt(enc, secret=key2, converter=converter)


def test_encrypt_decrypt_invalid_state_1():
    state = InterviewState(
        target_url="http://localhost",
        submission_id="s1",
        expiration_date=datetime(2020, 1, 1, tzinfo=timezone.utc),
        context={
            "test": True,
        },
        data={
            "test2": 2,
        },
    )

    key = os.urandom(32)

    enc = bytearray(state.encrypt(secret=key, converter=converter))

    enc[128] = (enc[128] + 1) % 256

    with pytest.raises(InvalidStateError):
        state.decrypt(enc, secret=key, converter=converter)


def test_encrypt_decrypt_invalid_state_2():
    state = InterviewState(
        target_url="http://localhost",
        submission_id="s1",
        expiration_date=datetime(2020, 1, 1, tzinfo=timezone.utc),
        context={
            "test": True,
        },
        data={
            "test2": 2,
        },
    )

    key = os.urandom(32)

    enc = state.encrypt(secret=key, converter=converter) + b"\x01\x00\x00\x00\x00"

    with pytest.raises(InvalidStateError):
        state.decrypt(enc, secret=key, converter=converter)


def test_state_expiration():
    state = InterviewState(
        target_url="http://localhost",
        submission_id="s1",
        expiration_date=datetime(2020, 1, 1, tzinfo=timezone.utc),
        context={
            "test": True,
        },
        data={
            "test2": 2,
        },
    )

    assert state.get_is_expired()
