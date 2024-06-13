"""Service module."""

from datetime import datetime

from loguru import logger
from oes.auth.auth import Authorization, AuthRepo
from oes.auth.config import Config
from oes.auth.token import (
    DEFAULT_REFRESH_TOKEN_LIFETIME,
    GUEST_REFRESH_TOKEN_LIFETIME,
    REFRESH_TOKEN_REUSE_GRACE_PERIOD,
    AccessToken,
    RefreshToken,
    RefreshTokenRepo,
    TokenError,
)
from sqlalchemy.ext.asyncio import AsyncSession


class AccessTokenService:
    """Access token service."""

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

    def __init__(self, repo: RefreshTokenRepo, auth_repo: AuthRepo, db: AsyncSession):
        self.repo = repo
        self.auth_repo = auth_repo
        self.db = db

    async def create(self, authorization: Authorization) -> RefreshToken:
        """Create a new refresh token for an authorization."""
        now = datetime.now().astimezone()
        # TODO: revisit this
        exp = now + (
            DEFAULT_REFRESH_TOKEN_LIFETIME
            if authorization.email
            else GUEST_REFRESH_TOKEN_LIFETIME
        )
        exp = (
            min(exp, authorization.date_expires) if authorization.date_expires else exp
        )

        current = await self.repo.get(authorization.id)
        if current:
            await self.repo.delete(current)

        token = RefreshToken(
            auth_id=authorization.id,
            date_created=now,
            date_expires=exp,
            authorization=authorization,
        )
        self.repo.add(token)
        return token

    async def refresh(self, token_str: str) -> RefreshToken:
        """Get an updated refresh token."""
        now = datetime.now().astimezone()
        auth_id, token_value = _split_token_str(token_str)
        auth = await self.auth_repo.get(auth_id, lock=True)
        if not auth:
            raise TokenError("No auth found")

        token = await self.repo.get(auth_id)
        if not token:
            raise TokenError("Refresh token not found")
        elif not token.is_valid(now=now):
            raise TokenError("Refresh token is expired")
        elif token.token != token_value:
            if now >= token.date_created + REFRESH_TOKEN_REUSE_GRACE_PERIOD:
                logger.warning(f"Revoked token for {auth.id} due to re-use")
                await self.revoke_token(token)
                await self.db.commit()
            raise TokenError("Token value did not match")

        new_token = await self.create(auth)

        return new_token

    async def revoke_token(self, token: RefreshToken):
        """Revoke a token."""
        await self.db.delete(token)


def _split_token_str(token_str: str) -> tuple[str, str]:
    auth_id, _, token = token_str.partition("-")
    return auth_id, token
