"""Serialization module."""

from cattrs import Converter

from oes.registration.registration import (
    Registration,
    RegistrationCreate,
    RegistrationUpdate,
    make_registration_create_structure_fn,
    make_registration_structure_fn,
    make_registration_unstructure_fn,
    make_registration_update_structure_fn,
)


def configure_converter(converter: Converter):
    """Configure a :class:`Converter`."""
    converter.register_structure_hook(
        Registration, make_registration_structure_fn(converter)
    )
    converter.register_structure_hook(
        RegistrationUpdate,
        make_registration_update_structure_fn(converter),
    )
    converter.register_structure_hook(
        RegistrationCreate,
        make_registration_create_structure_fn(converter),
    )
    converter.register_unstructure_hook(
        Registration,
        make_registration_unstructure_fn(converter),
    )
