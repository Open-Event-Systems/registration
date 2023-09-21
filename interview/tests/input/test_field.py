from unittest.mock import create_autospec, patch

from cattrs.preconf.json import make_converter
from importlib_metadata import EntryPoint
from oes.interview.input.field import get_class_for_field_type, structure_field
from oes.interview.input.field_types.text import TextField
from oes.interview.input.types import Field
from oes.interview.variables.locator import Locator, parse_locator
from oes.template import Template, structure_template

converter = make_converter()

converter.register_structure_hook_func(
    lambda cls: cls is Field, lambda v, t: structure_field(converter, v, t)
)
converter.register_structure_hook(Template, structure_template)
converter.register_structure_hook(Locator, lambda v, t: parse_locator(v))


class _Nested:
    @staticmethod
    def func(self):
        pass


@patch("oes.interview.input.field.importlib_metadata")
def test_get_class_for_field_type(mock):
    mock_ep = create_autospec(EntryPoint)
    mock_ep.name = "test"
    mock_ep.value = "tests.input.test_field:_Nested.func"

    mock.entry_points.return_value = [
        mock_ep,
    ]

    res = get_class_for_field_type("test")
    assert res is _Nested.func


def test_structure_field():
    config = {
        "type": "text",
        "set": "name",
        "label": "Name",
        "min": 2,
        "max": 20,
    }

    res = converter.structure(config, Field)
    assert res == TextField(
        set=parse_locator("name"),
        label=Template("Name"),
        min=2,
        max=20,
    )
