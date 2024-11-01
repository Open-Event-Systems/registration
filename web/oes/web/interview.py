"""Interview service."""

from collections.abc import Callable, Mapping, Sequence
from typing import Any, Literal, TypeVar

import httpx
import oes.web.registration
import orjson
from attrs import evolve, field, fields, frozen
from cattrs import Converter, override
from cattrs.gen import make_dict_structure_fn, make_dict_unstructure_fn
from cattrs.preconf.orjson import make_converter
from oes.utils.mapping import merge_mapping
from oes.web.config import Config, Event

_T = TypeVar("_T")


@frozen
class InterviewRegistrationFields:
    """Interview registration fields."""

    id: str | None = None
    event_id: str | None = None
    status: Literal["pending", "created", "canceled"] = "created"
    version: int = 1
    extra_data: Mapping[str, Any] = field(factory=dict)


@frozen
class InterviewRegistration:
    """A registration from an interview."""

    registration: InterviewRegistrationFields = InterviewRegistrationFields()
    """Interview registration fields."""

    meta: Mapping[str, Any] = field(factory=dict)
    """Cart metadata."""

    extra_data: Mapping[str, Any] = field(factory=dict)


@frozen
class CompletedInterview:
    """Completed interview body."""

    target: str
    event_id: str
    cart_id: str
    interview_id: str
    access_code: str | None = None
    meta: Mapping[str, Any] = field(factory=dict)
    context: Mapping[str, Any] = field(factory=dict)
    registration: InterviewRegistrationFields | None = None
    registrations: Sequence[InterviewRegistration] = ()

    data: Mapping[str, Any] = field(factory=dict)


class InterviewService:
    """Interview service."""

    def __init__(self, config: Config, client: httpx.AsyncClient):
        self.config = config
        self.client = client

    async def start_interview(
        self,
        event: Event,
        interview_id: str,
        cart_id: str,
        host: str,
        target: str,
        account_id: str | None,
        email: str | None,
        registration: Mapping[str, Any] | None,
        context: Mapping[str, Any] | None,
        initial_data: Mapping[str, Any] | None,
    ) -> Mapping[str, Any]:
        """Start an interview."""
        if registration is None:
            registration = {
                "id": oes.web.registration.generate_registration_id(),
                "status": "created",
                "event_id": event.id,
                "version": 1,
                "account_id": account_id,
            }

        full_context = merge_mapping(
            {
                "event": event.get_template_context(),
                "event_id": event.id,
                "interview_id": interview_id,
                "cart_id": cart_id,
                "email": email,
            },
            context if context is not None else {},
        )

        full_data = merge_mapping(
            {
                "registration": {
                    **registration,
                    "account_id": account_id or registration.get("account_id"),
                },
                "meta": {},
            },
            initial_data if initial_data is not None else {},
        )

        url = f"{self.config.interview_service_url}/interviews/{interview_id}"
        body = {
            "context": full_context,
            "data": full_data,
            "target": target,
        }

        body_bytes = orjson.dumps(body)
        res = await self.client.post(
            url,
            content=body_bytes,
            headers={"Content-Type": "application/json", "Host": host},
        )
        res.raise_for_status()
        return res.json()

    async def get_completed_interview(self, state: str) -> CompletedInterview | None:
        """Get a completed interview."""
        res = await self.client.get(
            f"{self.config.interview_service_url}/completed-interviews/{state}"
        )
        if res.status_code == 404:
            return None
        res.raise_for_status()
        return converter.structure(res.json(), CompletedInterview)


def _make_interview_structure_fn(
    c: Converter,
) -> Callable[[Any, Any], CompletedInterview]:
    def structure(v: Mapping[str, Any], t: Any) -> CompletedInterview:
        data = v["data"]
        context = v["context"]
        target = v["target"]
        meta = data.get("meta", {})
        cart_id = context["cart_id"]
        interview_id = context["interview_id"]
        event_id = context["event_id"]
        access_code = context.get("access_code")
        registration = data.get("registration")
        registrations = data.get("registrations", ())

        return CompletedInterview(
            target,
            event_id,
            cart_id,
            interview_id,
            access_code,
            meta,
            context,
            (
                c.structure(registration, InterviewRegistrationFields)
                if registration is not None
                else None
            ),
            c.structure(registrations, tuple[InterviewRegistration, ...]),
            data,
        )

    return structure


def _make_structure_with_extra_data_fn(
    cl: type[_T], c: Converter
) -> Callable[[Any, Any], _T]:
    fields_ = frozenset(f.name for f in fields(cl) if f.name != "extra_data")
    dict_fn = make_dict_structure_fn(cl, c, extra_data=override(omit=True))

    def structure(v: Mapping[str, Any], t: Any) -> _T:
        obj = dict_fn(v, t)
        extra_data = {k: v for k, v in v.items() if k not in fields_}
        return evolve(obj, extra_data=extra_data)

    return structure


def _make_unstructure_with_extra_data_fn(
    cl: type[_T], c: Converter
) -> Callable[[_T], Mapping[str, Any]]:
    dict_fn = make_dict_unstructure_fn(cl, c, extra_data=override(omit=True))

    def unstructure(v: _T) -> Mapping[str, Any]:
        data = dict_fn(v)
        return {**getattr(v, "extra_data", {}), **data}

    return unstructure


converter = make_converter()
converter.register_structure_hook(
    InterviewRegistrationFields,
    _make_structure_with_extra_data_fn(InterviewRegistrationFields, converter),
)
converter.register_unstructure_hook(
    InterviewRegistrationFields,
    _make_unstructure_with_extra_data_fn(InterviewRegistrationFields, converter),
)

converter.register_structure_hook(
    InterviewRegistration,
    _make_structure_with_extra_data_fn(InterviewRegistration, converter),
)
converter.register_unstructure_hook(
    InterviewRegistration,
    _make_unstructure_with_extra_data_fn(InterviewRegistration, converter),
)

converter.register_structure_hook(
    CompletedInterview,
    _make_interview_structure_fn(converter),
)
