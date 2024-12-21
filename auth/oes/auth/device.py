"""Device auth module."""

import secrets
from collections.abc import Mapping
from datetime import datetime, timedelta
from typing import Literal

import nanoid
from attrs import frozen
from oes.auth.auth import Authorization, AuthRepo, Scope, Scopes
from oes.auth.config import Config, RoleConfig
from oes.auth.orm import Base
from oes.auth.service import RefreshTokenService
from oes.auth.token import RefreshToken
from oes.utils.orm import Repo
from sqlalchemy import ForeignKey, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing_extensions import Self

DEVICE_CODE_LEN = 12
"""Device code length."""

USER_CODE_LEN = 8
"""User code length."""

EXPIRATION_TIME = timedelta(minutes=5)
"""Expiration time."""


@frozen
class DeviceAuthOptions:
    """Device auth authorization options."""

    role: str | None = None
    email: str | None = None
    anonymous: bool = False
    scope: Scopes | None = None
    date_expires: datetime | None = None
    path_length: int = 0


class DeviceAuth(Base):
    """Device auth entity."""

    __tablename__ = "device_auth"

    device_code: Mapped[str] = mapped_column(String(DEVICE_CODE_LEN), primary_key=True)
    user_code: Mapped[str] = mapped_column(String(USER_CODE_LEN), unique=True)
    date_expires: Mapped[datetime]
    auth_id: Mapped[str | None] = mapped_column(
        ForeignKey("auth.id"), nullable=True, default=None
    )

    authorization: Mapped[Authorization | None] = relationship(
        "Authorization", default=None
    )

    @classmethod
    def create(cls, *, now: datetime | None = None) -> Self:
        """Create a device auth entity."""
        now = now or datetime.now().astimezone()
        return cls(_make_device_code(), _make_user_code(), now + EXPIRATION_TIME)

    def get_is_valid(self, *, now: datetime | None = None) -> bool:
        """Get whether the auth is valid."""
        now = now or datetime.now().astimezone()
        return now < self.date_expires


class DeviceAuthRepo(Repo[DeviceAuth, str]):
    """Device auth repo."""

    entity_type = DeviceAuth

    async def get_by_user_code(
        self, user_code: str, *, lock: bool = False
    ) -> DeviceAuth | None:
        """Get by user code."""
        q = select(DeviceAuth).where(DeviceAuth.user_code == user_code.upper())

        if lock:
            q = q.with_for_update()

        res = await self.session.execute(q)
        return res.scalar()


class DeviceAuthService:
    """Device auth service."""

    def __init__(
        self,
        db: AsyncSession,
        repo: DeviceAuthRepo,
        auth_repo: AuthRepo,
        refresh_token_service: RefreshTokenService,
        config: Config,
    ):
        self.db = db
        self.repo = repo
        self.auth_repo = auth_repo
        self.refresh_token_service = refresh_token_service
        self.config = config

    async def create_auth(self) -> DeviceAuth:
        """Create a device auth entity."""
        entity = DeviceAuth.create()
        self.repo.add(entity)
        return entity

    async def check_auth(
        self, parent_auth_id: str, user_code: str
    ) -> Mapping[str, RoleConfig] | None:
        """Check a user code."""
        parent_auth = await self.auth_repo.get(parent_auth_id)
        if not parent_auth or not parent_auth.get_is_valid():
            return None

        entity = await self.repo.get_by_user_code(user_code)
        if entity is None or not entity.get_is_valid():
            return None
        await self.db.refresh(entity, ("authorization",))
        if entity.authorization is not None:
            return None
        if Scope.set_role not in parent_auth.scope:
            return {}

        return {
            r: cfg
            for r, cfg in self.config.roles.items()
            if cfg.can_use(parent_auth.scope)
        }

    async def authorize(  # noqa: CCR001
        self, user_code: str, parent_auth_id: str, options: DeviceAuthOptions
    ) -> bool | None:
        """Authorize a device."""
        parent_auth = await self.auth_repo.get(parent_auth_id)
        if (
            not parent_auth
            or not parent_auth.get_is_valid()
            or not parent_auth.can_create_child
        ):
            return False

        device_auth = await self.repo.get_by_user_code(user_code, lock=True)
        if not device_auth or not device_auth.get_is_valid():
            return None

        await self.db.refresh(device_auth, ("authorization",))
        if device_auth.authorization is not None:
            return False

        params = {}

        if options.date_expires:
            params["date_expires"] = options.date_expires

        if Scope.set_email in parent_auth.scope:
            if options.anonymous:
                params["email"] = None
            elif options.email:
                params["email"] = options.email

        if Scope.set_role in parent_auth.scope:
            if options.role:
                role_cfg = self.config.roles.get(options.role)
                if role_cfg and role_cfg.can_use(parent_auth.scope):
                    params["role"] = options.role
                else:
                    params["role"] = None
            else:
                params["role"] = None

        child = parent_auth.create_child(
            scope=options.scope if options.scope is not None else parent_auth.scope,
            path_length=options.path_length,
            **params
        )
        self.auth_repo.add(child)

        device_auth.authorization = child
        return True

    async def complete_auth(
        self, device_code: str
    ) -> RefreshToken | Literal[False] | None:
        """Attempt to complete device auth."""
        auth = await self.repo.get(device_code, lock=True)
        if not auth or not auth.get_is_valid():
            return None

        await self.db.refresh(auth, ("authorization",))
        if not auth.authorization:
            return False

        refresh_token = await self.refresh_token_service.create(auth.authorization)
        await self.repo.delete(auth)
        return refresh_token


def _make_device_code() -> str:
    return nanoid.generate(size=DEVICE_CODE_LEN)


def _make_user_code() -> str:
    return "".join(secrets.choice(_alphabet) for _ in range(USER_CODE_LEN))


_alphabet = "BCDFGHJKLMNPQRSTVWXYZ23456789"
