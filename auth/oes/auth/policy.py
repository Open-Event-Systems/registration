"""Endpoint policies."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Literal, Union
from urllib.parse import urlparse

from oes.auth.auth import Scope, Scopes
from typing_extensions import TypeAlias

PolicyNodeKey: TypeAlias = Union[
    Literal["*"],
    Literal["/"],
    str,
]

PolicyNode: TypeAlias = Union[
    Callable[[tuple[str, ...], str, Scopes], bool],
    str,
    "PolicyTree",
    None,
]


class _NotFound(ValueError):
    pass


PolicyTree: TypeAlias = Mapping[PolicyNodeKey, PolicyNode]


POLICY: PolicyTree = {
    "events": {
        # list/view events requires admin
        "/": Scope.admin,
        # /events/<event_id>
        "*": {
            "/": Scope.admin,
            # /events/<event_id>/registrations
            "registrations": {
                "/": (
                    lambda p, m, s: m == "POST"
                    and Scope.registration_write in s
                    or m in ("HEAD", "OPTIONS", "GET")
                    and Scope.registration in s
                ),
                # /events/<event_id>/registrations/<registration_id>
                "*": {
                    "/": (
                        lambda p, m, s: (
                            (Scope.registration in s)
                            if m in ("HEAD", "OPTIONS", "GET")
                            else (Scope.registration_write in s)
                        )
                    ),
                    "complete": Scope.registration_write,
                    "cancel": Scope.registration_write,
                    "assign-number": Scope.registration_write,
                    "documents": {
                        "/": Scope.registration,
                        "*": {
                            "*": Scope.registration,
                        },
                    },
                    # /events/<event_id>/registrations/<registration_id>
                    # /self-service/change/<interview_id>
                    "self-service": {"change": {"*": Scope.selfservice}},
                },
            },
            "update-registrations": (
                lambda p, m, s: True
            ),  # requires valid interview state
            "document-types": Scope.admin,
            "access-codes": {
                "/": (lambda p, m, s: m == "POST" and Scope.admin_write in s),
                # /events/<event_id>/access-codes/<code>
                "*": {
                    "check": (
                        lambda p, m, s: m in ("GET", "HEAD", "OPTIONS")
                        and Scope.selfservice in s
                    ),
                },
            },
            "self-service": {
                "add-registration": {
                    # /events/<event_id>/self-service/add-registration/<interview_id>
                    "*": Scope.selfservice
                }
            },
        },
    },
    "carts": {
        "empty": Scope.cart,
        # /carts/<cart_id>
        "*": {
            "/": Scope.admin,
            "add": (lambda p, m, s: True),  # requires valid interview state
            "registrations": {
                "/": (lambda p, m, s: m == "POST" and Scope.admin_write in s),
                "*": (lambda p, m, s: m == "DELETE" and Scope.cart in s),
            },
            "pricing-result": Scope.cart,
            "payment-methods": Scope.cart,
            "create-payment": Scope.cart,
            "self-service": {
                "add": {
                    # /carts/<cart_id>/self-service/add/<interview_id>
                    "*": (lambda p, m, s: Scope.selfservice in s and Scope.cart in s),
                },
                "change": {
                    "*": {
                        # /carts/<cart_id>/self-service/change/<registration_id>
                        # /<interview_id>
                        "*": (
                            lambda p, m, s: Scope.selfservice in s and Scope.cart in s
                        ),
                    }
                },
            },
        },
    },
    "payments": {
        "/": Scope.registration,
        "*": {
            "update": Scope.cart,
            "cancel": Scope.cart,
        },
    },
    "receipts": {
        "*": (lambda p, m, s: True),
    },
    "self-service": {
        "events": {"/": Scope.selfservice, "*": {"registrations": Scope.selfservice}},
    },
}


def is_allowed(method: str, url: str, scope: Scopes) -> bool:
    urlparts = urlparse(url)
    parts = tuple(p for p in urlparts.path.split("/") if p)
    try:
        node = _traverse(POLICY, parts)
    except _NotFound:
        return False

    if node is None:
        return True
    elif isinstance(node, str):
        return node in scope
    elif callable(node):
        return node(parts, method, scope)
    else:
        return False


def _traverse(
    tree: PolicyTree,
    parts: tuple[str, ...],
) -> PolicyNode:
    if len(parts) == 0:
        return _get_node(tree, "/")
    child: PolicyNode = tree
    for part in parts:
        child = _get_node(child, part)
    if isinstance(child, Mapping):
        return _get_node(child, "/")
    else:
        return child


def _get_node(tree: PolicyNode, part: str) -> PolicyNode:
    if not isinstance(tree, Mapping):
        raise _NotFound
    elif part in tree:
        return tree[part]
    elif "*" in tree:
        return tree["*"]
    else:
        raise _NotFound
