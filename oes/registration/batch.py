"""Batch changes."""

from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from oes.registration.registration import (
    Registration,
    RegistrationBatchChangeFields,
    RegistrationRepo,
)


class BatchChangeService:
    """Service for checking and applying changes in batches."""

    def __init__(self, session: AsyncSession, repo: RegistrationRepo):
        self.session = session
        self.repo = repo

    async def check(
        self, event_id: str, changes: Sequence[RegistrationBatchChangeFields]
    ) -> Sequence[Registration]:
        """Check that a batch of changes can be applied.

        Returns:
            A sequence of registration entities with mismatched versions.
        """
        current_regs = await self.repo.get_multi(
            (c.id for c in changes if c.id), event_id=event_id
        )
        return self._check_versions(changes, current_regs)

    async def apply(
        self, event_id: str, changes: Sequence[RegistrationBatchChangeFields]
    ) -> tuple[Sequence[Registration], Sequence[Registration]]:
        """Check and apply a batch of changes.

        Returns:
            A pair of sequences of completed changes or registrations with
            mismatched versions.
        """
        current_regs = await self.repo.get_multi(
            (c.id for c in changes if c.id), event_id=event_id, lock=True
        )
        failing = self._check_versions(changes, current_regs)
        if failing:
            return (), failing

        current_by_id = {cur.id: cur for cur in current_regs}

        results = tuple(
            c.apply(current_by_id.get(c.id) if c.id else None) for c in changes
        )

        for res in results:
            self.session.add(res)

        await self.session.flush()

        return results, ()

    def _check_versions(
        self,
        changes: Sequence[RegistrationBatchChangeFields],
        current: Sequence[Registration],
    ) -> Sequence[Registration]:
        change_vers = {c.id: c.version for c in changes if c.id}
        return tuple(cur for cur in current if cur.version != change_vers.get(cur.id))
