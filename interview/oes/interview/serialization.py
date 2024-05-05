"""Serialization module."""

from pathlib import Path
from typing import Union

from cattrs import Converter
from cattrs.preconf.orjson import make_converter

converter = make_converter()


def configure_converter(converter: Converter):
    """Configure a :class:`Converter`."""
    from oes.interview.config.interview import (
        InterviewConfigObject,
        make_interview_config_structure_fn,
    )

    converter.register_structure_hook(
        Union[Path, InterviewConfigObject],
        make_interview_config_structure_fn(converter),
    )
