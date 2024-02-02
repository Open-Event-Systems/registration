from cattrs.preconf.json import make_converter
from oes.interview.input.field import make_field_structure_fn
from oes.interview.input.field_types.text import TextField
from oes.interview.input.types import Field
from oes.interview.logic import ValuePointer, parse_pointer
from oes.template import Template, structure_template

converter = make_converter()

converter.register_structure_hook_func(
    lambda cls: cls is Field, make_field_structure_fn(converter)
)
converter.register_structure_hook(Template, structure_template)
converter.register_structure_hook(ValuePointer, lambda v, t: parse_pointer(v))


class _Nested:
    @staticmethod
    def func(self):
        pass


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
        set=parse_pointer("name"),
        label=Template("Name"),
        min=2,
        max=20,
    )
