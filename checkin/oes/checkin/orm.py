"""ORM module."""

from oes.utils.orm import NAMING_CONVENTION, TYPE_ANNOTATION_MAP
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Base(MappedAsDataclass, DeclarativeBase):
    """ORM base."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    type_annotation_map = TYPE_ANNOTATION_MAP


def import_entities():
    """Import all entities (used by migrations)."""
    from oes.checkin import checkin  # noqa
