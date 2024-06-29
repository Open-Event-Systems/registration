from datetime import datetime, timedelta

from oes.auth.auth import Authorization
from oes.auth.token import RefreshToken  # noqa


def test_is_valid():
    now = datetime.now().astimezone()
    exp = now + timedelta(hours=1)
    test_t = now + timedelta(hours=2)

    auth = Authorization(
        id="1",
        account_id="1",
        date_created=now,
        date_expires=exp,
    )

    assert auth.get_is_valid(now=now) is True
    assert auth.get_is_valid(now=test_t) is False


def test_can_create_child():
    auth = Authorization(
        id="1",
        account_id="1",
        path_length=1,
    )

    assert auth.can_create_child
    auth.path_length = 0
    assert not auth.can_create_child


def test_create_child_inherit():
    now = datetime.now().astimezone()
    exp = now + timedelta(hours=1)
    auth = Authorization(
        id="1",
        account_id="1",
        name="test",
        email="test@test.com",
        date_created=now,
        date_expires=exp,
        scope=frozenset(("a", "b")),
        path_length=2,
    )

    child = auth.create_child()
    assert child.date_expires == exp
    assert child.email == "test@test.com"
    assert child.name == "test"
    assert child.path_length == 1


def test_create_child_replace():
    now = datetime.now().astimezone()
    exp = now + timedelta(hours=1)
    auth = Authorization(
        id="1",
        account_id="1",
        name="test",
        email="test@test.com",
        date_created=now,
        date_expires=exp,
        scope=frozenset(("a", "b")),
        path_length=2,
    )

    child = auth.create_child(
        name="test2",
        email="test2@test.com",
        date_expires=now + timedelta(minutes=1),
        scope=frozenset(("a",)),
        path_length=0,
    )

    assert child.email == "test2@test.com"
    assert child.name == "test2"
    assert child.date_expires == now + timedelta(minutes=1)
    assert child.scope == frozenset(("a",))
    assert child.path_length == 0


def test_create_child_replace_combine():
    now = datetime.now().astimezone()
    exp = now + timedelta(hours=1)
    auth = Authorization(
        id="1",
        account_id="1",
        name="test",
        email="test@test.com",
        date_created=now,
        date_expires=exp,
        scope=frozenset(("a", "b")),
        path_length=2,
    )

    child = auth.create_child(
        date_expires=now + timedelta(days=1),
        scope=frozenset(("b", "c", "d")),
        path_length=5,
    )

    assert child.date_expires == now + timedelta(hours=1)
    assert child.scope == frozenset(("b",))
    assert child.path_length == 1
