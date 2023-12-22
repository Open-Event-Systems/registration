"""Queue functions."""
import re

from oes.registration.checkout.service import CheckoutService


def _parse_receipt_url(url: str) -> tuple[str, int]:
    match = re.match(r"/([a-z0-9]+)(?:#r([0-9]+))?$", url, re.I)
    if not match:
        return "", 0
    elif match.group(2):
        return match.group(1), int(match.group(2)) - 1
    else:
        return match.group(1), 0


async def _get_reg_id_by_receipt(receipt_id: str, index: int, service: CheckoutService):
    checkout = await service.get_checkout_by_receipt_id(receipt_id)
    if not checkout:
        return None
    cart_data = checkout.get_cart_data()
    try:
        return cart_data.registrations[index].id
    except IndexError:
        return None
