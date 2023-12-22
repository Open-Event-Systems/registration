"""Event models."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date  # noqa
from typing import TYPE_CHECKING, Optional

from attrs import Factory, field, frozen
from oes.registration.models.identifier import validate_identifier
from oes.registration.models.logic import Whenable, WhenCondition
from oes.template import Template, ValueOrEvaluable
from typing_extensions import Self

if TYPE_CHECKING:
    from oes.registration.auth.user import User


@frozen(kw_only=True)
class RegistrationOption:
    """A registration option."""

    id: str = field(validator=validate_identifier)
    """The option ID."""

    type_id: Optional[Template] = None
    """A type ID for the option."""

    name: str
    """The option name."""

    description: Optional[str] = None
    """The option description."""


@frozen(kw_only=True)
class ModifierRule(Whenable):
    """Event line item modifier rule."""

    type_id: Optional[Template] = None
    """A type ID for the modifier."""

    name: Template
    """The modifier name."""

    amount: int
    """The amount."""

    when: WhenCondition
    """The condition/conditions when the modifier applies."""


@frozen(kw_only=True)
class LineItemRule(Whenable):
    """Event line item pricing rule."""

    type_id: Optional[Template] = None
    """A type ID for the line item."""

    name: Template
    """The line item name."""

    description: Optional[Template] = None
    """The line item description."""

    price: int
    """The price."""

    modifiers: Sequence[ModifierRule] = ()
    """Modifier rules."""

    when: WhenCondition
    """The condition/conditions when the line item is present."""


@frozen
class RegistrationDisplayOptions:
    """Display options for a registration in the self-service view."""

    title: Template = Template("{{registration.display_name}}")
    subtitle: Template = Template("")
    description: Template = Template("")


@frozen
class EventDisplayOptions:
    """Display options."""

    registration: RegistrationDisplayOptions = RegistrationDisplayOptions()
    """The template for how to display a registration in the self-service view."""


@frozen
class EventInterviewOption(Whenable):
    """An available event interview."""

    id: str
    """The interview ID."""

    when: WhenCondition = ()
    """The condition."""


@frozen
class QueueConfig:
    """Queue configuration."""

    priority: ValueOrEvaluable = 1
    """Expression for a registration's priority."""

    tags: Mapping[str, WhenCondition] = field(factory=dict)
    """Mapping of tags to ``when`` conditions."""

    features: Mapping[str, ValueOrEvaluable] = field(factory=dict)
    """Mapping of registration features to expressions of their weights."""


@frozen(kw_only=True)
class Event:
    """Event class."""

    id: str = field(validator=validate_identifier)
    """The event ID."""

    name: str
    """The event name."""

    description: Optional[str] = None
    """The event description."""

    date: date
    """The event start date."""

    open: bool = False
    """Whether the event is open."""

    visible: bool = False
    """Whether the event is visible."""

    registration_options: Sequence[RegistrationOption] = ()
    """The registration options."""

    add_interviews: Sequence[EventInterviewOption] = ()
    """The interviews available for adding a new registration."""

    change_interviews: Sequence[EventInterviewOption] = ()
    """The interviews available for changing an existing registration."""

    check_in_interview: str
    """The interview to use for check-in."""

    pricing_rules: Sequence[LineItemRule] = ()
    """Line item pricing rules."""

    display_options: EventDisplayOptions = EventDisplayOptions()
    """Display options."""

    queue: QueueConfig = QueueConfig()
    """Queue configuration."""

    def is_visible_to(self, user: Optional[User]) -> bool:
        """Get whether the event is visible to the given user."""
        return self.visible or user and user.is_admin

    def is_open_to(self, user: Optional[User]) -> bool:
        """Get whether the event is open to the given user."""
        return self.open and self.is_visible_to(user) or user and user.is_admin


@frozen(kw_only=True)
class SimpleEventInfo:
    """A subset of event information sent to things like pricing hooks."""

    id: str
    name: str
    description: Optional[str] = None
    date: date
    open: bool = False
    visible: bool = False
    registration_options: Sequence[RegistrationOption] = ()

    @classmethod
    def create(cls, event: Event) -> Self:
        """Create from a :class:`Event`."""
        return cls(
            id=event.id,
            name=event.name,
            description=event.description,
            date=event.date,
            open=event.open,
            visible=event.visible,
            registration_options=tuple(event.registration_options),
        )


@frozen
class EventConfig:
    """Event configuration."""

    events: Sequence[Event]

    _events_by_id: dict[str, Event] = field(
        init=False,
        eq=False,
        default=Factory(lambda s: {e.id: e for e in s.events}, takes_self=True),
    )

    def get_event(self, id: str) -> Optional[Event]:
        """Get an event by ID."""
        return self._events_by_id.get(id)
