import pytest
from oes.interview.input.field_types.text import TextFieldTemplate
from oes.interview.input.question import QuestionTemplate
from oes.interview.interview.resolve import (
    get_question_template_providing_indirect_path,
    get_question_template_providing_path,
    index_question_templates_by_indirect_path,
    index_question_templates_by_path,
)
from oes.interview.logic.pointer import parse_pointer

questions = [
    ("q1", QuestionTemplate(fields=(TextFieldTemplate(set=parse_pointer("a.a")),))),
    (
        "q2",
        QuestionTemplate(
            fields=(
                TextFieldTemplate(set=parse_pointer("a.b")),
                TextFieldTemplate(set=parse_pointer("a.c")),
            )
        ),
    ),
    (
        "q3",
        QuestionTemplate(
            fields=(
                TextFieldTemplate(set=parse_pointer("a.a")),
                TextFieldTemplate(set=parse_pointer("a.d")),
            ),
            when=False,
        ),
    ),
    ("q4", QuestionTemplate(fields=(TextFieldTemplate(set=parse_pointer("b.a")),))),
    ("q5", QuestionTemplate(fields=(TextFieldTemplate(set=parse_pointer("b.a")),))),
    (
        "q6",
        QuestionTemplate(fields=(TextFieldTemplate(set=parse_pointer("c[value]")),)),
    ),
    ("q7", QuestionTemplate(fields=(TextFieldTemplate(set=parse_pointer("c[0]")),))),
    (
        "q8",
        QuestionTemplate(fields=(TextFieldTemplate(set=parse_pointer("d[value]")),)),
    ),
    (
        "q9",
        QuestionTemplate(
            fields=(TextFieldTemplate(set=parse_pointer("e[value][value]")),)
        ),
    ),
    (
        "q10",
        QuestionTemplate(fields=(TextFieldTemplate(set=parse_pointer("e[value][0]")),)),
    ),
    (
        "q11",
        QuestionTemplate(fields=(TextFieldTemplate(set=parse_pointer("e[0][value]")),)),
    ),
]


@pytest.mark.parametrize(
    "provide, asked_ids, expected_id",
    [
        (("a", "a"), set(), "q1"),
        (("a", "b"), set(), "q2"),
        (("a", "c"), set(), "q2"),
        (("b", "a"), set(), "q4"),
        (("b", "a"), {"q4"}, "q5"),
        (("c", 0), set(), "q7"),
    ],
)
def test_resolve_questions(provide, asked_ids, expected_id):
    index = index_question_templates_by_path(questions)
    res = get_question_template_providing_path(provide, {"value": 0}, asked_ids, index)
    res_id = res[0] if res else None
    assert res_id == expected_id


@pytest.mark.parametrize(
    "provide, asked_ids, expected_id",
    [
        (("c", 0), set(), "q6"),
        (("e", 0, 0), set(), "q11"),
        (("e", 0, 0), {"q11"}, "q9"),
        (("e", 0, 0), {"q11", "q9"}, "q10"),
    ],
)
def test_resolve_questions_indirect(provide, asked_ids, expected_id):
    index = index_question_templates_by_indirect_path(questions)
    res = get_question_template_providing_indirect_path(
        provide, {"value": 0}, asked_ids, index
    )
    res_id = res[0] if res else None
    assert res_id == expected_id
