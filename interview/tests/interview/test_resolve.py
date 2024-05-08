import pytest
from oes.interview.input.field_types.text import TextFieldTemplate
from oes.interview.input.question import QuestionTemplate
from oes.interview.interview.error import InterviewError
from oes.interview.interview.interview import make_interview_context
from oes.interview.interview.resolve import (
    resolve_question_providing_path,
    resolve_undefined_values,
)
from oes.interview.interview.state import InterviewState
from oes.interview.logic.env import default_jinja2_env
from oes.interview.logic.pointer import parse_pointer
from oes.utils.template import Expression, Template

questions = {
    "q1": QuestionTemplate(fields={parse_pointer("a.a"): TextFieldTemplate()}),
    "q2": QuestionTemplate(
        fields={
            parse_pointer("a.b"): TextFieldTemplate(),
            parse_pointer("a.c"): TextFieldTemplate(),
        },
    ),
    "q3": QuestionTemplate(
        fields={
            parse_pointer("a.a"): TextFieldTemplate(),
            parse_pointer("a.d"): TextFieldTemplate(),
        },
        when=False,
    ),
    "q4": QuestionTemplate(fields={parse_pointer("b.a"): TextFieldTemplate()}),
    "q5": QuestionTemplate(fields={parse_pointer("b.a"): TextFieldTemplate()}),
    # QuestionTemplate(
    #     id="q6", fields=(TextFieldTemplate(set=parse_pointer("c[value]")),)
    # ),
    # QuestionTemplate(id="q7", fields=(TextFieldTemplate(set=parse_pointer("c[0]")),)),
    # QuestionTemplate(
    #     id="q8", fields=(TextFieldTemplate(set=parse_pointer("d[value]")),)
    # ),
    # QuestionTemplate(
    #     id="q9", fields=(TextFieldTemplate(set=parse_pointer("e[value][value]")),)
    # ),
    # QuestionTemplate(
    #     id="q10", fields=(TextFieldTemplate(set=parse_pointer("e[value][0]")),)
    # ),
    # QuestionTemplate(
    #     id="q11", fields=(TextFieldTemplate(set=parse_pointer("e[0][value]")),)
    # ),
}


@pytest.mark.parametrize(
    "provide, asked_ids, expected_id",
    [
        (("a", "a"), set(), "q1"),
        (("a", "b"), set(), "q2"),
        (("a", "c"), set(), "q2"),
        (("b", "a"), set(), "q4"),
        (("b", "a"), {"q4"}, "q5"),
        # (("c", 0), set(), "q7"),
        # (("c", 0), {"q7"}, "q6"),
        # (("e", 0, 0), set(), "q11"),
        # (("e", 0, 0), {"q11"}, "q9"),
        # (("e", 0, 0), {"q11", "q9"}, "q10"),
    ],
)
def test_resolve_questions(provide, asked_ids, expected_id):
    interview_context = make_interview_context(
        questions, [], InterviewState(data={"value": 0})
    )
    id, _, _ = resolve_question_providing_path(provide, interview_context, asked_ids)
    assert id == expected_id


questions2 = {
    "q1": QuestionTemplate(
        fields={
            parse_pointer("a"): TextFieldTemplate(),
        },
    ),
    "q2": QuestionTemplate(
        fields={
            parse_pointer("b"): TextFieldTemplate(),
        },
        when=Expression("a", default_jinja2_env),
    ),
    "q3": QuestionTemplate(
        description=Template("{{ b }}", default_jinja2_env),
        fields={
            parse_pointer("c"): TextFieldTemplate(),
        },
    ),
    "q4": QuestionTemplate(
        description=Template("{{ recursive }}", default_jinja2_env),
        fields={
            parse_pointer("recursive"): TextFieldTemplate(),
        },
    ),
    "q5": QuestionTemplate(
        description=Template("{{ q6 }}", default_jinja2_env),
        fields={
            parse_pointer("q5"): TextFieldTemplate(),
        },
    ),
    "q6": QuestionTemplate(
        description=Template("{{ q5 }}", default_jinja2_env),
        fields={
            parse_pointer("q6"): TextFieldTemplate(),
        },
    ),
    # QuestionTemplate(
    #     id="q7",
    #     fields=(TextFieldTemplate(set=parse_pointer("n")),),
    # ),
    # QuestionTemplate(
    #     id="q8",
    #     fields=(TextFieldTemplate(set=parse_pointer("p[n]")),),
    # ),
    # QuestionTemplate(
    #     id="q9",
    #     fields=(TextFieldTemplate(set=parse_pointer("p[n].name")),),
    # ),
    # QuestionTemplate(
    #     id="q10",
    #     description=Template("{{ p[n].name }}", default_jinja2_env),
    #     fields=(TextFieldTemplate(set=parse_pointer("p[n].other")),),
    # ),
}


@pytest.mark.parametrize(
    "eval, data, expected_id",
    [
        ("b", {}, "q1"),
        ("c", {}, "q1"),
        ("c", {"a": True}, "q2"),
        ("c", {"b": "b"}, "q3"),
        # ("p[0].name", {"p": []}, "q7"),
        # ("p[0].name", {"p": [], "n": 0}, "q8"),
        # ("p[0].name", {"p": [{}], "n": 0}, "q9"),
        # ("p[0].other", {"p": [{}], "n": 0}, "q9"),
        # ("p[0].other", {"p": [{"name": "..."}], "n": 0}, "q10"),
    ],
)
def test_resolve_context(eval, data, expected_id):
    expr = Expression(eval, default_jinja2_env)
    interview_context = make_interview_context(
        questions2, [], InterviewState(data=data)
    )
    with resolve_undefined_values(interview_context) as resolver:
        bool(expr.evaluate(interview_context.state.template_context))
    assert resolver.result[0] == expected_id


@pytest.mark.parametrize(
    "eval, data",
    [
        ("x", {}),
        ("c", {"a": False}),
        ("recursive", {}),
        ("q5", {}),
        ("q6", {}),
    ],
)
def test_resolve_context_errors(eval, data):
    expr = Expression(eval, default_jinja2_env)
    interview_context = make_interview_context(
        questions2, [], InterviewState(data=data)
    )
    with pytest.raises(InterviewError), resolve_undefined_values(interview_context):
        bool(expr.evaluate(interview_context.state.template_context))
