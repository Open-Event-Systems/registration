"""Endpoint policies."""

from urllib.parse import urlparse

from oes.auth.auth import Scope, Scopes


async def is_allowed(method: str, url: str, scope: Scopes) -> bool:  # noqa: CCR001
    """Get whether a request is allowed."""
    parsed = urlparse(url)
    path = parsed.path
    parts = _split_path(path)

    # /self-service
    if len(parts) >= 1 and parts[0] == "self-service":
        return Scope.selfservice in scope

    # /events/<event_id>
    elif len(parts) >= 3 and parts[0] == "events":
        if parts[2] == "registrations":
            return await _check_registration_routes(method, scope)
        elif parts[2] == "access-codes" and len(parts) >= 5 and parts[4] == "check":
            return method in ("GET", "HEAD", "OPTIONS") and Scope.selfservice in scope
        elif parts[2] == "access-codes" and len(parts) == 3:
            return method == "POST" and Scope.admin in scope

    # /carts/<cart_id>
    elif len(parts) >= 2 and parts[0] == "carts":  # noqa: SIM114
        return Scope.cart in scope

    # /payments/<payment_id>
    elif (
        len(parts) >= 3 and parts[0] == "payments" and parts[2] in ("update", "cancel")
    ):  # noqa: SIM114
        return Scope.cart in scope

    return False


async def _check_registration_routes(method: str, scope: Scopes) -> bool:
    if method in ("PUT", "POST", "PATCH", "DELETE"):
        return Scope.registration_write in scope
    else:
        return Scope.registration in scope


def _split_path(path: str) -> list[str]:
    path = path[:-1] if path.endswith("/") else path
    path = path if path.startswith("/") else f"/{path}"
    return path.split("/")[1:]
