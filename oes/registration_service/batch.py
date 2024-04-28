"""Batch changes."""

from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from oes.registration_service.event import EventStatsService
from oes.registration_service.registration import (
    Registration,
    RegistrationBatchChangeFields,
    RegistrationRepo,
    Status,
)


class BatchChangeService:
    """Service for checking and applying changes in batches."""

    def __init__(
        self,
        session: AsyncSession,
        repo: RegistrationRepo,
        event_stats_service: EventStatsService,
    ):
        self.session = session
        self.repo = repo
        self.event_stats_service = event_stats_service

    async def check(
        self,
        event_id: str,
        changes: Sequence[RegistrationBatchChangeFields],
        *,
        lock: bool = False,
    ) -> tuple[list[Registration], list[Registration]]:
        """Check that a batch of changes can be applied.

        Returns:
            A pair of sequences of valid registrations and registrations with
            mismatched versions.
        """
        current_regs = await self.repo.get_multi(
            (c.id for c in changes if c.id), event_id=event_id, lock=lock
        )
        failed_ver = self._check_versions(changes, current_regs)
        failed_status = self._check_status(changes, current_regs)
        failed = [
            cur for cur in current_regs if cur in failed_ver or cur in failed_status
        ]
        return list(current_regs), failed

    async def apply(
        self,
        event_id: str,
        changes: Sequence[RegistrationBatchChangeFields],
        current: Sequence[Registration],
    ) -> list[Registration]:
        """Apply a batch of changes.

        Returns:
            A sequences of created/updated registrations.
        """
        current_by_id = {cur.id: cur for cur in current}

        results = [c.apply(current_by_id.get(c.id) if c.id else None) for c in changes]

        for res in results:
            self.session.add(res)

        to_assign = [
            r for r in results if r.status == Status.created and r.number is None
        ]

        with self.session.no_autoflush:
            await self.event_stats_service.assign_numbers(event_id, to_assign)

        await self.session.flush()

        return results

    def _check_versions(
        self,
        changes: Sequence[RegistrationBatchChangeFields],
        current: Sequence[Registration],
    ) -> list[Registration]:
        change_vers = {c.id: c.version for c in changes if c.id}
        return [cur for cur in current if cur.version != change_vers.get(cur.id)]

    def _check_status(
        self,
        changes: Sequence[RegistrationBatchChangeFields],
        current: Sequence[Registration],
    ) -> list[Registration]:
        new_status = {c.id: c.status for c in changes}
        return [
            cur
            for cur in current
            if cur.status != new_status[cur.id]
            and new_status[cur.id] not in _allowable_status_changes[cur.status]
        ]


_allowable_status_changes = {
    Status.pending: (Status.created, Status.canceled),
    Status.created: (Status.canceled,),
    Status.canceled: (),
}
