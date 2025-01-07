"""Payment service."""

from collections.abc import Mapping, Sequence
from typing import Any

import httpx
from oes.web.cart import CartService
from oes.web.config import Config
from oes.web.registration import RegistrationService


class PaymentService:
    """Payment service."""

    def __init__(
        self,
        cart_service: CartService,
        registration_service: RegistrationService,
        client: httpx.AsyncClient,
        config: Config,
    ):
        self.cart_service = cart_service
        self.registration_service = registration_service
        self.client = client
        self.config = config

    async def get_payment_options(
        self,
        cart_id: str,
        user_role: str | None,
    ) -> Sequence[Mapping[str, Any]] | None:
        """Get payment options."""
        cart = await self.cart_service.get_cart(cart_id)
        if not cart:
            return None
        pricing_result = await self.cart_service.get_pricing_result(cart_id)
        cart_data = cart.get("cart")
        headers = {}

        if user_role:
            headers["x-role"] = user_role

        body = {
            "cart_id": cart_id,
            "cart_data": cart_data,
            "pricing_result": pricing_result,
        }
        res = await self.client.post(
            f"{self.config.payment_service_url}/payment-methods",
            json=body,
            headers=headers,
        )
        if res.status_code == 404:
            return None
        res.raise_for_status()
        return res.json()

    async def create_payment(
        self,
        cart_id: str,
        method: str,
        email: str | None,
        user_role: str | None,
    ) -> tuple[int, Mapping[str, Any]] | None:
        """Create a payment.

        Returns:
            A pair of a status code and body, or None if not found.
        """
        cart = await self.cart_service.get_cart(cart_id)
        if not cart:
            return None
        pricing_result = await self.cart_service.get_pricing_result(cart_id)
        cart_data = cart.get("cart", {})
        updated_data = [r["new"] for r in cart_data["registrations"]]
        access_codes = {
            r["id"]: r["meta"]["access_code"]
            for r in cart_data["registrations"]
            if "meta" in r and r["meta"].get("access_code")
        }

        headers = {}

        body = {
            "cart_id": cart_id,
            "cart_data": cart_data,
            "pricing_result": pricing_result,
        }

        check_res, check_body = await self.registration_service.check_batch_change(
            cart_data.get("event_id", ""), updated_data, access_codes
        )
        if check_res != 200:
            return check_res, check_body

        if email:
            headers["x-email"] = email

        if user_role:
            headers["x-role"] = user_role

        res = await self.client.post(
            f"{self.config.payment_service_url}/payments",
            json=body,
            params={"method": method},
            headers=headers,
        )
        if res.status_code == 404:
            return None
        res.raise_for_status()
        return res.status_code, res.json()

    async def get_payment(self, payment_id: str) -> Mapping[str, Any] | None:
        """Get a payment by ID."""
        res = await self.client.get(
            f"{self.config.payment_service_url}/payments/{payment_id}"
        )
        if res.status_code == 404:
            return None
        res.raise_for_status()
        return res.json()

    async def update_payment(
        self, payment_id: str, body: Mapping[str, Any]
    ) -> tuple[int, Mapping[str, Any]] | None:
        """Update a payment.

        Returns:
            A pair of a status code and body, or None if not found.
        """
        payment = await self.get_payment(payment_id)
        if payment is None:
            return None
        cart_data = payment.get("cart_data", {})
        updated_data = [r["new"] for r in cart_data["registrations"]]
        access_codes = {
            r["id"]: r["meta"]["access_code"]
            for r in cart_data["registrations"]
            if "meta" in r and r["meta"].get("access_code")
        }

        apply_res, apply_body = await self.registration_service.apply_batch_change(
            cart_data.get("event_id", ""), updated_data, access_codes, payment_id, body
        )
        return apply_res, apply_body
