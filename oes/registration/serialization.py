"""Serialization module."""

from uuid import UUID

from cattrs import Converter

from oes.registration.registration import (
    Registration,
    RegistrationBatchChangeFields,
    RegistrationCreateFields,
    RegistrationUpdateFields,
    make_registration_fields_structure_fn,
    make_registration_unstructure_fn,
)


def configure_converter(converter: Converter):
    """Configure a :class:`Converter`."""
    converter.register_structure_hook(
        UUID, lambda v, t: v if isinstance(v, UUID) else UUID(v)
    )

    converter.register_structure_hook(
        Registration, make_registration_fields_structure_fn(Registration, converter)
    )
    converter.register_structure_hook(
        RegistrationCreateFields,
        make_registration_fields_structure_fn(RegistrationCreateFields, converter),
    )
    converter.register_structure_hook(
        RegistrationUpdateFields,
        make_registration_fields_structure_fn(RegistrationUpdateFields, converter),
    )
    converter.register_structure_hook(
        RegistrationBatchChangeFields,
        make_registration_fields_structure_fn(RegistrationUpdateFields, converter),
    )
    converter.register_unstructure_hook(
        Registration,
        make_registration_unstructure_fn(converter),
    )
