"""Auth handlers."""
from collections.abc import Callable
from typing import Any, Optional
from uuid import UUID

from blacksheep import Request
from blacksheep.exceptions import Forbidden
from blacksheep.server.bindings import Binder, BoundValue
from guardpost import Identity, Policy
from guardpost.asynchronous.authentication import AuthenticationHandler
from guardpost.authorization import AuthorizationContext
from guardpost.synchronous.authorization import Requirement
from jwt import InvalidTokenError
from oes.registration.auth.scope import Scope, Scopes
from oes.registration.auth.token import AccessToken
from oes.registration.auth.user import User, UserIdentity
from oes.registration.models.config import Config


class TokenAuthHandler(AuthenticationHandler):
    """Handler to allow the web server to use token auth."""

    def __init__(self, config: Config):
        self.config = config

    async def authenticate(self, context: Request) -> Optional[Identity]:
        token_val = _get_token(context)
        token = (
            _decode_token(token_val, key=self.config.auth.signing_key)
            if token_val
            else None
        )

        if token:
            user = UserIdentity(
                id=UUID(token.sub) if token.sub else None,
                email=token.email,
                scope=token.scope,
                expiration_date=token.exp,
                client_id=token.azp,
            )
            context.identity = user
            return user
        else:
            context.identity = None
            return None


def _get_token(request: Request) -> Optional[str]:
    header = request.get_first_header(b"Authorization")
    if not header:
        return None

    typ, _, value = header.partition(b" ")
    if typ.lower() != b"bearer":
        return None

    return value.decode()


def _decode_token(value: str, *, key: str) -> Optional[AccessToken]:
    try:
        token = AccessToken.decode(value, key=key)
    except InvalidTokenError:
        return None

    return token


class ScopeRequirement(Requirement):
    """Require a scope."""

    def __init__(self, *scopes: Scope):
        self.scopes = Scopes(scopes)

    def handle(self, context: AuthorizationContext):
        identity = context.identity

        if not identity:
            context.fail("Missing identity")
            return

        if not isinstance(identity, UserIdentity) or not any(
            s in identity.scope for s in self.scopes
        ):
            context.fail(f"Missing one of scopes: {self.scopes!r}")
            # workaround: the authorization framework returns 401 instead of 403...
            raise Forbidden

        context.succeed(self)


RequireAdmin = "require_admin"
RequireCart = "require_cart"
RequireCheckout = "require_checkout"
RequireEvent = "require_event"
RequireSelfService = "require_self_service"
RequireRegistration = "require_registration"
RequireRegistrationEdit = "require_registration_edit"
RequireRegistrationEditOrAction = "require_registration_edit_or_action"
RequireRegistrationAction = "require_registration_action"
RequireCheckIn = "require_check_in"
RequireSelfServiceOrKiosk = "require_self_service_or_kiosk"

require_admin = Policy(RequireAdmin, ScopeRequirement(Scope.admin))
require_cart = Policy(RequireCart, ScopeRequirement(Scope.cart))
require_checkout = Policy(RequireCheckout, ScopeRequirement(Scope.checkout))
require_event = Policy(RequireEvent, ScopeRequirement(Scope.event))
require_self_service = Policy(RequireSelfService, ScopeRequirement(Scope.self_service))
require_registration = Policy(RequireRegistration, ScopeRequirement(Scope.registration))
require_registration_edit = Policy(
    RequireRegistrationEdit, ScopeRequirement(Scope.registration_edit)
)
require_registration_action = Policy(
    RequireRegistrationAction, ScopeRequirement(Scope.registration_action)
)
require_registration_edit_or_action = Policy(
    RequireRegistrationEditOrAction,
    ScopeRequirement(
        Scope.registration_edit,
        Scope.registration_action,
    ),
)
require_check_in = Policy(RequireCheckIn, ScopeRequirement(Scope.check_in))
require_self_service_or_kiosk = Policy(
    RequireSelfServiceOrKiosk, ScopeRequirement(Scope.self_service, Scope.kiosk)
)


class RequestUser(BoundValue[User]):
    """Bound value for the app specific :class:`User` interface."""

    pass


class UserBinder(Binder):
    """User binder.

    Even though not explicitly used, this is required to support implicitly binding
    :class:`User`.
    """

    handle = RequestUser
    type_alias = User

    def __init__(
        self,
        expected_type: Any = User,
        name: str = "",
        implicit: bool = True,
        required: bool = True,
        converter: Optional[Callable] = None,
    ):
        super().__init__(expected_type, name, implicit, required, converter)

    async def get_value(self, request: Request) -> Optional[User]:
        return getattr(request, "identity", None)
