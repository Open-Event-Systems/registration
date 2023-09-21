import copy

import pytest
from cattrs.preconf.json import make_converter

from oes.template.template import Template, structure_template, unstructure_template

converter = make_converter()
converter.register_structure_hook(Template, structure_template)
converter.register_unstructure_hook(Template, unstructure_template)


@pytest.mark.parametrize(
    "src, context, value",
    [
        ("normal", {}, "normal"),
        ("{{ test }}", {"test": "text"}, "text"),
        ("{{ test }}", {}, ""),
    ],
)
def test_template(src, context, value):
    template = Template(src)
    res = template.render(context)
    assert res == value


def test_copy():
    a = Template("{{ test }}")
    b = copy.deepcopy(a)
    assert a == b


def test_convert():
    tmpl = Template("{{ test }}")
    as_str = converter.unstructure(tmpl)
    assert as_str == "{{ test }}"
    other = converter.structure(as_str, Template)
    assert other == tmpl
