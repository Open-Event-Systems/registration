"""Health check script."""

from datetime import datetime, timedelta

import httpx
from oes.auth.auth import Scope
from oes.auth.config import get_config
from oes.auth.token import AccessToken

config = get_config()

res = httpx.get("http://localhost:8000/_healthcheck")
res.raise_for_status()

token = AccessToken(
    iss="oes",
    typ="at",
    exp=datetime.now().astimezone() + timedelta(seconds=5),
    sub="<healthcheck>",
    email="test@example.net",
    scope=frozenset((Scope.selfservice,)),
)
auth_str = f"Bearer {token.encode(key=config.token_secret)}"

res = httpx.get(
    "http://localhost:8000/auth/validate",
    headers={"Authorization": auth_str, "x-original-uri": "/self-service/events"},
)
res.raise_for_status()
email = res.headers.get("x-email")
account_id = res.headers.get("x-account-id")
assert account_id == "<healthcheck>"
assert email == "test@example.net"
