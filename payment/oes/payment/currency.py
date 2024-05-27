"""Currency utils."""

CURRENCY_DECIMALS = {
    "BHD": 3,
    "BIF": 0,
    "CLF": 4,
    "CLP": 0,
    "DJF": 0,
    "GNF": 0,
    "IQD": 3,
    "ISK": 0,
    "JOD": 3,
    "JPY": 0,
    "KMF": 0,
    "KRW": 0,
    "KWD": 3,
    "LYD": 3,
    "OMR": 3,
    "PYG": 0,
    "RWF": 0,
    "TND": 3,
    "UGX": 0,
    "UYI": 0,
    "UYW": 4,
    "VND": 0,
    "VUV": 0,
    "XAF": 0,
    "XAG": 0,
    "XAU": 0,
    "XBA": 0,
    "XBB": 0,
    "XBC": 0,
    "XBD": 0,
    "XDR": 0,
    "XOF": 0,
    "XPD": 0,
    "XPF": 0,
    "XPT": 0,
    "XSU": 0,
    "XTS": 0,
    "XUA": 0,
    "XXX": 0,
}
"""Decimal places of currency codes, if not 2."""


def format_currency(currency: str, amount: int) -> str:
    """Format a currency value."""
    dec = CURRENCY_DECIMALS.get(currency.upper(), 2)
    as_dec = amount * pow(10, -dec)
    return f"{as_dec:.{dec}f}"
