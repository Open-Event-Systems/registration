"""WebAuthn module."""

import base64
import secrets
from collections.abc import Mapping
from datetime import datetime, timedelta
from typing import Any, Literal
from urllib.parse import urlparse

from attrs import frozen
from oes.auth.auth import Authorization, AuthRepo
from oes.auth.config import Config
from oes.auth.orm import Base
from oes.auth.token import TokenBase, TokenError
from oes.utils.orm import Repo
from sqlalchemy import ForeignKey, Text, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from typing_extensions import Self
from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    helpers,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.authentication.verify_authentication_response import (
    VerifiedAuthentication,
)
from webauthn.helpers.exceptions import (
    InvalidAuthenticationResponse,
    InvalidRegistrationResponse,
)
from webauthn.helpers.structs import (
    AttestationConveyancePreference,
    AuthenticatorAttachment,
    AuthenticatorSelectionCriteria,
    PublicKeyCredentialDescriptor,
    ResidentKeyRequirement,
)
from webauthn.registration.verify_registration_response import VerifiedRegistration


@frozen
class WebAuthnRegistrationChallenge(TokenBase):
    """WebAuthn registration challenge."""

    typ: Literal["wrc"]
    sub: str
    auth_id: str

    @classmethod
    def create(cls, auth_id: str, email: str, config: Config) -> tuple[Self, str]:
        """Create a registration challenge."""
        challenge_bytes = secrets.token_bytes(16)
        challenge_str = _b64encode(challenge_bytes)
        opts = generate_registration_options(
            rp_id=_origin_to_rp_id(config.origin),
            rp_name=config.name,
            user_id=auth_id.encode(),
            user_name=email,
            user_display_name=email,
            challenge=challenge_bytes,
            timeout=180000,
            attestation=AttestationConveyancePreference.NONE,
            authenticator_selection=AuthenticatorSelectionCriteria(
                authenticator_attachment=AuthenticatorAttachment.PLATFORM,
                resident_key=ResidentKeyRequirement.DISCOURAGED,
            ),
        )
        json_str = helpers.options_to_json(opts)
        return (
            cls(
                iss="oes",
                typ="wrc",
                sub=challenge_str,
                auth_id=auth_id,
                exp=datetime.now().astimezone() + timedelta(seconds=180),
            ),
            json_str,
        )

    def verify(
        self, body: Mapping[str, Any], config: Config
    ) -> VerifiedRegistration | None:
        """Verify a registration challenge."""
        challenge_bytes = _b64decode(self.sub)
        try:
            return verify_registration_response(
                credential=dict(body),
                expected_challenge=challenge_bytes,
                expected_rp_id=_origin_to_rp_id(config.origin),
                expected_origin=config.origin,
            )
        except InvalidRegistrationResponse:
            return None


@frozen
class WebAuthnAuthenticationChallenge(TokenBase):
    """WebAuthn authentication challenge."""

    typ: Literal["wac"]
    sub: str
    cr_id: str

    @classmethod
    def create(cls, credential_id: str, config: Config) -> tuple[Self, str]:
        """Create an authentication challenge."""
        challenge_bytes = secrets.token_bytes(16)
        challenge_str = _b64encode(challenge_bytes)
        credential_id_bytes = _b64decode(credential_id)
        opts = generate_authentication_options(
            rp_id=_origin_to_rp_id(config.origin),
            challenge=challenge_bytes,
            timeout=180000,
            allow_credentials=[
                PublicKeyCredentialDescriptor(id=credential_id_bytes),
            ],
        )
        json_str = helpers.options_to_json(opts)
        return (
            cls(
                iss="oes",
                typ="wac",
                sub=challenge_str,
                cr_id=credential_id,
                exp=datetime.now().astimezone() + timedelta(seconds=180),
            ),
            json_str,
        )

    def verify(
        self, public_key: str, sign_count: int, body: Mapping[str, Any], config: Config
    ) -> VerifiedAuthentication | None:
        """Verify an authentication challenge."""
        challenge_bytes = _b64decode(self.sub)
        public_key_bytes = _b64decode(public_key)
        try:
            return verify_authentication_response(
                credential=dict(body),
                expected_challenge=challenge_bytes,
                expected_rp_id=_origin_to_rp_id(config.origin),
                expected_origin=config.origin,
                credential_public_key=public_key_bytes,
                credential_current_sign_count=sign_count,
            )
        except InvalidAuthenticationResponse:
            return None


class WebAuthnCredential(Base):
    """WebAuthn credential."""

    __tablename__ = "webauthn_credential"

    auth_id: Mapped[str] = mapped_column(ForeignKey("auth.id"), primary_key=True)
    credential_id: Mapped[str] = mapped_column(unique=True)
    public_key: Mapped[str] = mapped_column(Text)
    sign_count: Mapped[int]

    authorization: Mapped[Authorization] = relationship(
        "Authorization", back_populates="webauthn_credential"
    )

    @classmethod
    def create(cls, auth: Authorization, registration: VerifiedRegistration) -> Self:
        """Create a credential from a verified registration."""
        return cls(
            auth_id=auth.id,
            credential_id=_b64encode(registration.credential_id),
            public_key=_b64encode(registration.credential_public_key),
            sign_count=registration.sign_count,
            authorization=auth,
        )


class WebAuthnCredentialRepo(Repo[WebAuthnCredential, str]):
    """WebAuthnCredential repo."""

    entity_type = WebAuthnCredential

    async def get_by_credential_id(
        self, id: str, *, lock: bool = False
    ) -> WebAuthnCredential | None:
        """Get a credential by ID."""
        if lock:
            q = (
                select(Authorization)
                .where(Authorization.id == id)
                .with_for_update()
                .options(
                    selectinload(
                        Authorization.refresh_token, Authorization.webauthn_credential
                    )
                )
            )
        q = select(WebAuthnCredential).where(WebAuthnCredential.credential_id == id)
        if lock:
            q = q.with_for_update()
        q = q.options(selectinload(WebAuthnCredential.authorization))
        res = await self.session.execute(q)
        return res.scalar()


class WebAuthnService:
    """WebAuthn service."""

    def __init__(
        self, repo: WebAuthnCredentialRepo, auth_repo: AuthRepo, config: Config
    ):
        self.repo = repo
        self.auth_repo = auth_repo
        self.config = config

    def create_registration_challenge(self, auth: Authorization) -> tuple[str, str]:
        """Create a registration challenge.

        Returns:
            A pair of the challenge token and challenge JSON string.
        """
        if auth.email is None:
            raise ValueError("Email is required")
        challenge, challenge_str = WebAuthnRegistrationChallenge.create(
            auth_id=auth.id,
            email=auth.email,
            config=self.config,
        )
        encoded = challenge.encode(key=self.config.token_secret)
        return encoded, challenge_str

    def complete_registration(
        self, auth: Authorization, challenge_token: str, body: Mapping[str, Any]
    ) -> WebAuthnCredential | None:
        """Complete a registration."""
        now = datetime.now().astimezone()
        try:
            challenge = WebAuthnRegistrationChallenge.decode(
                challenge_token, key=self.config.token_secret
            )
        except TokenError:
            return None
        if challenge.exp <= now or challenge.auth_id != auth.id:
            return None
        result = challenge.verify(body, self.config)
        if result is None:
            return None
        entity = WebAuthnCredential.create(auth, result)
        self.repo.add(entity)
        return entity

    async def create_authentication_challenge(
        self, credential_id: str
    ) -> tuple[str, str] | None:
        """Create an authentication challenge.

        Returns:
            A pair of the challenge token and challenge JSON string.
        """
        credential = await self.repo.get_by_credential_id(credential_id)
        if not credential:
            return None
        challenge, challenge_str = WebAuthnAuthenticationChallenge.create(
            credential_id, self.config
        )
        encoded = challenge.encode(key=self.config.token_secret)
        return encoded, challenge_str

    async def complete_authentication(
        self, challenge_token: str, body: Mapping[str, Any]
    ) -> Authorization | None:
        """Complete authentcation."""
        now = datetime.now().astimezone()
        try:
            challenge = WebAuthnAuthenticationChallenge.decode(
                challenge_token, key=self.config.token_secret
            )
        except TokenError:
            return None
        if challenge.exp <= now:
            return None
        credential = await self.repo.get_by_credential_id(challenge.cr_id)
        if not credential:
            return None

        auth = await self.auth_repo.get(credential.auth_id, lock=True)
        if not auth:
            return None

        credential = await self.repo.get(auth.id, lock=True)
        if not credential:
            return None

        result = challenge.verify(
            credential.public_key, credential.sign_count, body, self.config
        )
        if not result:
            return None
        credential.sign_count += 1
        return auth


def _origin_to_rp_id(origin: str) -> str:
    parts = urlparse(origin)
    return parts.hostname or origin


def _b64encode(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def _b64decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "==")
