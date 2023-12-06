"""Device grant service module."""
from typing import Optional

from oes.registration.auth.account_service import AccountService
from oes.registration.auth.entities import AccountEntity, DeviceAuthEntity
from oes.registration.auth.scope import Scopes
from oes.registration.auth.user import User, UserIdentity
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class DeviceAuthService:
    """Device grant service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_device_auth(self, auth: DeviceAuthEntity):
        """Save a created :class:`DeviceAuthEntity`."""
        self.db.add(auth)
        await self.db.flush()

    async def get_by_device_code(self, device_code: str) -> Optional[DeviceAuthEntity]:
        """Get a :class:`DeviceAuthEntity` by device code."""
        return await self.db.get(DeviceAuthEntity, device_code)

    async def get_by_user_code(self, user_code: str) -> Optional[DeviceAuthEntity]:
        """Get a :class:`DeviceAuthEntity` by user code."""
        res = await self.db.execute(
            select(DeviceAuthEntity).where(DeviceAuthEntity.user_code == user_code)
        )
        return res.scalar()

    async def delete(self, auth: DeviceAuthEntity):
        """Delete a :class:`DeviceAuthEntity`."""
        await self.db.delete(auth)


async def authorize_device_auth(
    auth: DeviceAuthEntity,
    user: User,
    account_service: AccountService,
    new_account: bool = False,
    email: Optional[str] = None,
    scope: Optional[Scopes] = None,
    require_webauthn: bool = False,
) -> bool:
    """Authorize a device.

    Args:
        auth: The :class:`DeviceAuthEntity`.
        user: The authorizing user.
        account_service: The account service.
        new_account: Whether to create a new account instead of using the authorizer's.
        email: The email associated with the new account.
        scope: Overrides the granted scopes.
        require_webauthn: Require WebAuthn for a refresh token.

    Returns:
        True if the authorization was successful, otherwise False.
    """
    if not auth.is_valid() or auth.account_id is not None:
        return False

    requested_scope = Scopes(auth.scope)
    user_scope = user.scope

    combined_scope = Scopes(requested_scope & user_scope)

    if user.is_admin:
        override_scope = Scopes(scope) if scope is not None else combined_scope

        if new_account:
            account = await account_service.create_account(
                email=email, scope=override_scope
            )
            auth.account_id = account.id
        else:
            auth.account_id = user.id

        auth.require_webauthn = require_webauthn

        auth.scope = str(override_scope)
    else:
        auth.scope = str(combined_scope)
        auth.account_id = user.id

    return True


async def complete_device_auth(
    auth: DeviceAuthEntity,
    auth_service: DeviceAuthService,
    account_service: AccountService,
) -> Optional[UserIdentity]:
    """Complete device auth.

    Returns:
        A :class:`UserIdentity`, or None if not valid.
    """
    if not auth.is_valid() or auth.account_id is None:
        return None

    account = await account_service.get_account(auth.account_id)
    if not auth:
        return None

    user = UserIdentity(id=account.id, email=account.email, scope=Scopes(auth.scope))

    await auth_service.delete(auth)
    return user
