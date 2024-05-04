from oes.interview.immutable import make_immutable
from oes.interview.input.field_types.text import TextFieldTemplate
from oes.interview.input.question import QuestionTemplate
from oes.interview.logic.env import default_jinja2_env
from oes.interview.logic.pointer import parse_pointer
from oes.utils.template import Template


def test_question_schema():
    config = QuestionTemplate(
        id="test",
        title=Template("{{ title }}", default_jinja2_env),
        description="desc",
        fields=(
            TextFieldTemplate(
                set=parse_pointer("text"),
                label="field",
            ),
            TextFieldTemplate(
                set=parse_pointer("text"),
                label="field2",
                optional=True,
            ),
        ),
    )
    question = config.get_question({"title": "Test"})
    assert question.schema == make_immutable(
        {
            "type": "object",
            "title": "Test",
            "description": "desc",
            "properties": {
                "field_0": {
                    "type": "string",
                    "x-type": "text",
                    "title": "field",
                    "minLength": 0,
                    "maxLength": 300,
                },
                "field_1": {
                    "type": ["string", "null"],
                    "x-type": "text",
                    "title": "field2",
                    "minLength": 0,
                    "maxLength": 300,
                },
            },
            "required": ["field_0"],
        }
    )
