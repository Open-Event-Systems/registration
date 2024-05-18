from datetime import datetime, timedelta

import pytest
from oes.auth.token import AccessToken, TokenError


def test_encode_decode():
    now = datetime.now().astimezone().replace(microsecond=0)
    exp = now + timedelta(hours=1)
    tok = AccessToken("oes", exp, "at")
    enc = tok.encode(key="test")
    dec = tok.decode(enc, key="test")
    assert dec == tok


def test_decode_key_error():
    now = datetime.now().astimezone().replace(microsecond=0)
    exp = now + timedelta(hours=1)
    tok = AccessToken("oes", exp, "at")
    enc = tok.encode(key="test")
    with pytest.raises(TokenError):
        tok.decode(enc, key="wrong")


def test_decode_expired_error():
    now = datetime.now().astimezone().replace(microsecond=0)
    exp = now - timedelta(hours=1)
    tok = AccessToken("oes", exp, "at")
    enc = tok.encode(key="test")
    with pytest.raises(TokenError):
        tok.decode(enc, key="test")


def test_decode_type_error():
    now = datetime.now().astimezone().replace(microsecond=0)
    exp = now + timedelta(hours=1)
    tok = AccessToken("oes", exp, "X")  # type: ignore
    enc = tok.encode(key="test")
    with pytest.raises(TokenError):
        tok.decode(enc, key="test")


def test_decode_aud_error():
    now = datetime.now().astimezone().replace(microsecond=0)
    exp = now + timedelta(hours=1)
    tok = AccessToken("other", exp, "at")  # type: ignore
    enc = tok.encode(key="test")
    with pytest.raises(TokenError):
        tok.decode(enc, key="test")
