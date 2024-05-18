"""Service module."""

from datetime import datetime

from loguru import logger
from oes.auth.config import Config
from oes.auth.token import (
    DEFAULT_REFRESH_TOKEN_LIFETIME,
    GUEST_REFRESH_TOKEN_LIFETIME,
    REFRESH_TOKEN_REUSE_GRACE_PERIOD,
    AccessToken,
    RefreshToken,
    TokenError,
)
from sqlalchemy.ext.asyncio import AsyncSession


class AuthService:
    """Auth service."""

    def __init__(self, config: Config):
        self.config = config

    def validate_token(self, auth_header_str: str) -> AccessToken | None:
        """Validate the ``Authorization`` header."""
        method, _, token_str = auth_header_str.partition(" ")
        token_str = token_str.strip()
        if method.lower() != "bearer" or not token_str:
            return None

        try:
            decoded = AccessToken.decode(token_str, key=self.config.token_secret)
        except TokenError as exc:
            logger.debug(f"Invalid access token: {exc}")
            return None

        return decoded


class RefreshTokenService:
    """Refresh token service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, account_id: str | None = None, email: str | None = None
    ) -> RefreshToken:
        """Create a new refresh token."""
        now = datetime.now().astimezone()
        # TODO: revisit this
        exp = now + (
            DEFAULT_REFRESH_TOKEN_LIFETIME if email else GUEST_REFRESH_TOKEN_LIFETIME
        )
        token = RefreshToken(
            date_issued=now,
            date_expires=exp,
            account_id=account_id,
            email=email,
            date_last_used=now,
        )
        self.db.add(token)
        await self.db.flush()
        return token

    async def refresh(self, token_str: str) -> RefreshToken:
        """Get an updated refresh token."""
        now = datetime.now().astimezone()
        token_id, token_value = _split_token_str(token_str)
        token = await self.db.get(RefreshToken, token_id, with_for_update=True)
        if not token:
            raise TokenError("Refresh token not found")
        if not token.is_valid(now=now):
            raise TokenError("Refresh token is expired")

        if token.token != token_value:
            if now >= token.date_last_used + REFRESH_TOKEN_REUSE_GRACE_PERIOD:
                logger.warning(f"Revoked token {token.id} due to re-use")
                await self.revoke_token(token)
                await self.db.commit()
            raise TokenError("Token value did not match")

        # TODO: revisit this
        exp = now + (
            DEFAULT_REFRESH_TOKEN_LIFETIME
            if token.email
            else GUEST_REFRESH_TOKEN_LIFETIME
        )
        token.refresh(exp=exp, now=now)

        return token

    async def revoke_token(self, token: RefreshToken):
        """Revoke a token."""
        await self.db.delete(token)


def _split_token_str(token_str: str) -> tuple[str, str]:
    token_id, _, token = token_str.partition("-")
    return token_id, token
