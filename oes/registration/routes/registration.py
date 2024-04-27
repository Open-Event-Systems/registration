"""Registration routes."""

from collections.abc import Sequence
from blacksheep.exceptions import NotFound
from oes.registration.cattrs_binder import FromCattrs
from oes.registration.registration import (
    Registration,
    RegistrationCreate,
    RegistrationRepo,
)
from oes.registration.routes.router import router


@router.get("/registrations")
async def list_registrations(
    registration_repo: RegistrationRepo,
) -> Sequence[Registration]:
    """List registrations."""
    return await registration_repo.search()


@router.post("/registrations")
async def create_registration(
    repo: RegistrationRepo, body: FromCattrs[RegistrationCreate]
) -> Registration:
    """Create registrations."""
    reg = body.value.create()
    repo.add(reg)
    await repo.flush()
    return reg
