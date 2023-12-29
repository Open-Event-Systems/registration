"""Payment configuration objects."""
from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from typing import TYPE_CHECKING, Any, Optional

from attrs import frozen
from loguru import logger
from oes.registration.cart.models import CartData, PricingResult
from oes.registration.models.config import PaymentConfig, PaymentMethodConfigMapping
from oes.registration.models.logic import WhenCondition, when_matches
from oes.registration.payment.services.suspend import SuspendPaymentService
from oes.template import Expression

if TYPE_CHECKING:
    from oes.registration.payment.types import PaymentService


@frozen
class PaymentMethod:
    """A payment method."""

    id: str
    """The payment method ID."""

    name: str
    """A human-readable name."""

    service: str
    """The payment service ID this method uses."""

    config: Mapping[str, Any]
    """Payment method configuration settings."""

    when: WhenCondition = ()
    """The conditions when this method is allowed."""


class PaymentServices:
    """Payment services configuration object."""

    def __init__(
        self,
        services: Mapping[str, PaymentService],
        methods: Mapping[str, PaymentMethod],
    ):
        self._services = services
        self._methods = methods

    def get_services(self) -> Iterator[PaymentService]:
        """Get configured payment services."""
        return iter(self._services.values())

    def get_service(self, id: str) -> Optional[PaymentService]:
        """Get a :class:`PaymentService` by ID, or ``None`` if not found."""
        return self._services.get(id)

    def get_methods(self) -> Iterator[PaymentMethod]:
        """Get configured payment methods."""
        return iter(self._methods.values())

    def get_method(self, id: str) -> Optional[PaymentMethod]:
        """Get a :class:`PaymentMethod` by ID, or ``None`` if not found."""
        return self._methods.get(id)


def get_available_payment_methods(
    methods: Iterable[PaymentMethod],
    *,
    cart_data: CartData,
    pricing_result: PricingResult,
) -> Iterator[PaymentMethod]:
    """Get available payment methods for a cart."""
    yield from (
        m
        for m in methods
        if is_payment_method_available(
            m, cart_data=cart_data, pricing_result=pricing_result
        )
    )


def is_payment_method_available(
    method: PaymentMethod,
    *,
    cart_data: CartData,
    pricing_result: PricingResult,
) -> bool:
    """Return whether a payment method is available for the given cart."""
    ctx = {
        "cart_data": cart_data,
        "pricing_result": pricing_result,
    }
    return when_matches(method, ctx)


def create_payment_services(payment_config: PaymentConfig) -> PaymentServices:
    """Create a :class:`PaymentServices` object."""
    from .services.system import SystemPaymentService

    services = {}
    for id, config_data in payment_config.services.items():
        res = create_payment_service(id, config_data)
        if res is not None:
            services[id] = res

    services["system"] = SystemPaymentService()
    services["suspend"] = SuspendPaymentService()

    methods = {}

    for method_config in payment_config.methods:
        service_id = method_config["service"]
        if service_id not in services:
            logger.warning(
                f"Payment method {method_config['id']} uses nonexistent service "
                f"{service_id}"
            )
            continue
        method = create_payment_method(method_config)
        methods[method.id] = method

    methods["zero-balance"] = PaymentMethod(
        id="zero-balance",
        service="system",
        name="Complete Checkout",
        config={},
        when=Expression("pricing_result.total_price == 0"),
    )

    return PaymentServices(services, methods)


def create_payment_service(
    id: str, config_data: Mapping[str, Any]
) -> Optional[PaymentService]:
    """Get a payment service from a config."""
    if id == "mock":
        from .services.mock import create_mock_payment_service

        return create_mock_payment_service(config_data)
    elif id == "square":
        from .services.square import create_square_service

        return create_square_service(config_data)
    else:
        logger.warning(f"Unsupported payment service: {id}")
        return None


def create_payment_method(config_data: PaymentMethodConfigMapping) -> PaymentMethod:
    """Create a :class:`PaymentMethod` from configuration data."""
    config_dict = dict(config_data)
    return PaymentMethod(
        id=config_dict.pop("id"),
        service=config_dict.pop("service"),
        name=config_dict.pop("name"),
        when=config_dict.pop("when", ()),
        config=config_dict,
    )
