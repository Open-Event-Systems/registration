"""Error types."""


class PaymentServiceError(RuntimeError):
    """Raised when an operation with a payment service does not succeed."""

    pass


class CheckoutStateError(PaymentServiceError):
    """Raised when a checkout is in an invalid state."""

    pass


class CheckoutNotFoundError(PaymentServiceError):
    """Raised when a checkout is not found."""

    pass


class CheckoutCancelError(CheckoutStateError):
    """Raised when a checkout could not be canceled."""

    # TODO: remove

    pass


class ValidationError(ValueError, PaymentServiceError):
    """Raised when submitted checkout data does not validate."""

    pass
