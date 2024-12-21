from collections.abc import Iterable

import pytest
from oes.auth.auth import Scope
from oes.auth.policy import is_allowed


@pytest.mark.parametrize(
    "method, url, scope, expected",
    [
        ("GET", "/self-service/events", (Scope.selfservice,), True),
        ("GET", "/self-service/events", (), False),
        ("GET", "/events/example-event/registrations", (Scope.registration,), True),
        (
            "GET",
            "/events/example-event/registrations/reg-id",
            (Scope.registration,),
            True,
        ),
        ("GET", "/events/example-event/registrations", (), False),
        ("GET", "/events/example-event/registrations/reg-id", (), False),
        ("POST", "/events/example-event/registrations", (Scope.registration,), False),
        (
            "PUT",
            "/events/example-event/registrations/reg-id/cancel",
            (Scope.registration,),
            False,
        ),
        (
            "POST",
            "/events/example-event/registrations",
            (Scope.registration, Scope.registration_write),
            True,
        ),
        (
            "PUT",
            "/events/example-event/registrations/reg-id/cancel",
            (Scope.registration, Scope.registration_write),
            True,
        ),
        (
            "GET",
            "/events/example-event/access-codes",
            (Scope.selfservice, Scope.registration, Scope.registration_write),
            False,
        ),
        (
            "GET",
            "/events/example-event/access-codes/code",
            (Scope.selfservice, Scope.registration, Scope.registration_write),
            False,
        ),
        (
            "GET",
            "/events/example-event/access-codes/code/check",
            (Scope.selfservice, Scope.registration, Scope.registration_write),
            True,
        ),
        (
            "GET",
            "/carts/cart-id",
            (Scope.cart,),
            False,
        ),
        (
            "GET",
            "/carts/cart-id",
            (Scope.admin,),
            True,
        ),
        (
            "GET",
            "/carts/cart-id",
            (),
            False,
        ),
        (
            "GET",
            "/events/event-id/registrations/reg-id/unknown",
            (Scope.selfservice, Scope.registration_write, Scope.registration),
            False,
        ),
    ],
)
def test_policy(method: str, url: str, scope: Iterable[str], expected: bool):
    res = is_allowed(method, url, frozenset(scope))
    assert res is expected
