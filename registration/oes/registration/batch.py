"""Batch changes."""

from __future__ import annotations

import functools
from collections.abc import Callable, Mapping, Sequence
from enum import Enum
from typing import Any

import httpx
from attrs import define
from oes.registration.access_code import AccessCode, AccessCodeService
from oes.registration.event import EventStatsService
from oes.registration.registration import (
    Registration,
    RegistrationBatchChangeFields,
    RegistrationRepo,
    Status,
)
from sqlalchemy.ext.asyncio import AsyncSession


class ErrorCode(str, Enum):
    """Batch change failure error codes."""

    version = "version"
    status = "status"
    event = "event"
    access_code = "access_code"


@define
class BatchChangeResult:
    """The result of a batch change."""

    change: RegistrationBatchChangeFields
    errors: Sequence[ErrorCode] = ()


class BatchChangeService:
    """Service for checking and applying changes in batches."""

    def __init__(
        self,
        session: AsyncSession,
        repo: RegistrationRepo,
        event_stats_service: EventStatsService,
        access_code_service: AccessCodeService,
        client: httpx.AsyncClient,
    ):
        self.session = session
        self.repo = repo
        self.event_stats_service = event_stats_service
        self.access_code_service = access_code_service
        self.client = client

    async def check(
        self,
        event_id: str,
        changes: Sequence[RegistrationBatchChangeFields],
        access_codes: Mapping[str, str],
        *,
        lock: bool = False,
    ) -> tuple[
        dict[str, Registration],
        Mapping[str, AccessCode | None],
        list[BatchChangeResult],
    ]:
        """Check that a batch of changes can be applied."""
        current = {
            cur.id: cur
            for cur in await self.repo.get_multi(
                (c.id for c in changes), event_id=event_id, lock=lock
            )
        }
        access_code_entities = await self._get_access_codes(
            event_id, access_codes, lock=lock
        )
        return (
            current,
            access_code_entities,
            [
                self._check_change(
                    event_id,
                    current.get(c.id),
                    c,
                    access_codes.get(c.id),
                    access_code_entities.get(c.id),
                )
                for c in changes
            ],
        )

    async def apply(
        self,
        event_id: str,
        changes: Sequence[RegistrationBatchChangeFields],
        access_codes: Mapping[str, AccessCode | None],
        current: Mapping[str, Registration],
    ) -> list[Registration]:
        """Apply a batch of changes.

        Returns:
            A sequence of created/updated registrations.
        """
        # add new registrations first to trigger any concurrent inserts
        created_regs = [c.apply(None) for c in changes if c.id not in current]
        for created_reg in created_regs:
            self.session.add(created_reg)
        await self.session.flush()

        updated_regs = [c.apply(current[c.id]) for c in changes if c.id in current]

        to_assign = [
            r
            for r in (*created_regs, *updated_regs)
            if r.status == Status.created and r.number is None
        ]

        with self.session.no_autoflush:  # don't double-increment the version
            await self.event_stats_service.assign_numbers(event_id, to_assign)

        for code in access_codes.values():
            if code:
                code.used = True

        # restore original order
        results_by_id = {r.id: r for r in (*created_regs, *updated_regs)}
        return [results_by_id[c.id] for c in changes]

    async def complete_payment(
        self, payment_url: str, payment_body: Mapping[str, Any]
    ) -> tuple[int, Mapping[str, Any]]:
        """Complete a payment."""
        res = await self.client.post(payment_url, json=payment_body)
        return res.status_code, res.json()

    async def _get_access_codes(
        self, event_id: str, access_codes: Mapping[str, str], *, lock: bool = False
    ) -> Mapping[str, AccessCode | None]:
        ids = sorted(access_codes.items(), key=lambda x: x[1])
        entities = {
            reg_id: await self.access_code_service.get(event_id, code, lock=lock)
            for reg_id, code in ids
        }
        return entities

    def _check_change(
        self,
        event_id: str,
        registration: Registration | None,
        change: RegistrationBatchChangeFields,
        access_code: str | None,
        access_code_entity: AccessCode | None,
    ) -> BatchChangeResult:
        checks: list[Callable[[RegistrationBatchChangeFields], BatchChangeResult]] = [
            lambda c: _check_version(registration, c),
            lambda c: _check_status(registration, c),
            lambda c: _check_event(event_id, registration, c),
            lambda c: _check_access_code(
                access_code, access_code_entity, registration, c
            ),
        ]
        return functools.reduce(_apply_check, checks, BatchChangeResult(change))


_allowable_status_changes = {
    Status.pending: (Status.created, Status.canceled),
    Status.created: (Status.canceled,),
    Status.canceled: (),
}


def _apply_check(
    cur: BatchChangeResult,
    func: Callable[[RegistrationBatchChangeFields], BatchChangeResult],
) -> BatchChangeResult:
    res = func(cur.change)
    return BatchChangeResult(cur.change, [*cur.errors, *res.errors])


def _check_version(
    registration: Registration | None, change: RegistrationBatchChangeFields
) -> BatchChangeResult:
    return BatchChangeResult(
        change,
        (
            [ErrorCode.version]
            if registration and registration.version != change.version
            else []
        ),
    )


def _check_status(
    registration: Registration | None, change: RegistrationBatchChangeFields
) -> BatchChangeResult:
    cur_status = registration.status if registration else Status.pending
    return BatchChangeResult(
        change,
        (
            [ErrorCode.status]
            if change.status != cur_status
            and change.status not in _allowable_status_changes.get(cur_status, ())
            else []
        ),
    )


def _check_event(
    event_id: str,
    registration: Registration | None,
    change: RegistrationBatchChangeFields,
) -> BatchChangeResult:
    return BatchChangeResult(
        change,
        (
            [ErrorCode.event]
            if change.event_id != event_id
            or registration
            and registration.event_id != change.event_id
            else []
        ),
    )


def _check_access_code(
    access_code: str | None,
    access_code_entity: AccessCode | None,
    registration: Registration | None,
    change: RegistrationBatchChangeFields,
) -> BatchChangeResult:
    return BatchChangeResult(
        change,
        ([ErrorCode.access_code] if access_code and not access_code_entity else []),
    )
