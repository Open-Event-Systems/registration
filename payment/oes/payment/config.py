"""Config module."""

from collections.abc import Callable, Mapping
from importlib.metadata import entry_points
from typing import Any

import typed_settings as ts
from cattrs import Converter
from oes.payment.payment import PaymentMethodConfig
from oes.payment.types import PaymentService
from oes.utils.config import get_loaders
from sqlalchemy import URL, make_url

ENTRY_POINT_GROUP = "oes.payment.services"


@ts.settings
class Config:
    """Config file options."""

    db_url: URL = ts.option(
        default=make_url("postgresql+asyncpg:///payment"),
        converter=lambda v: make_url(v),
        help="the database URL",
    )

    services: Mapping[str, Mapping[str, Any]] = ts.option(
        factory=dict, help="payment service configuration"
    )
    methods: Mapping[str, PaymentMethodConfig] = ts.option(
        factory=dict, help="payment method config"
    )


def get_config() -> Config:
    """Get the config."""
    return ts.load_settings(
        Config, get_loaders("OES_PAYMENT_SERVICE_", ("payment.yml",))
    )


def get_payment_service_factory(
    service: str,
) -> Callable[[Mapping[str, Any], Converter], PaymentService]:
    """Get a :class:`PaymentService` factory."""
    ep = next(iter(entry_points(group=ENTRY_POINT_GROUP, name=service)), None)
    if ep is None:
        raise LookupError(f"No such payment service: {service}")
    factory = ep.load()
    return factory
