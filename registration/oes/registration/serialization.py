"""Serialization module."""

from cattrs import Converter
from oes.registration.registration import (
    Registration,
    RegistrationBatchChangeFields,
    RegistrationCreateFields,
    RegistrationUpdateFields,
    make_registration_fields_structure_fn,
    make_registration_unstructure_fn,
)
from oes.utils.serialization import configure_converter as _configure_converter


def configure_converter(converter: Converter):
    """Configure a :class:`Converter`."""
    _configure_converter(converter)

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
        make_registration_fields_structure_fn(RegistrationBatchChangeFields, converter),
    )
    converter.register_unstructure_hook(
        Registration,
        make_registration_unstructure_fn(converter),
    )
