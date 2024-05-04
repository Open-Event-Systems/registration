from oes.interview.immutable import make_immutable
from oes.interview.interview.state import InterviewState


def test_state_template_context():
    state = InterviewState(data={"a": 1, "b": [2, 3]}, context={"a": 2, "c": 3})
    assert state.template_context == make_immutable(
        {
            "a": 2,
            "b": [2, 3],
            "c": 3,
        }
    )


def test_state_update():
    state = InterviewState(data={"a": 1, "b": 2}, context={"ctx": "ctx"})
    updated = state.update(
        data={"b": 3, "ctx": "other"},
        completed=True,
        answered_question_ids=("1",),
    )
    assert updated.data == make_immutable({"b": 3, "ctx": "other"})
    assert updated.completed is True
    assert updated.answered_question_ids == frozenset(("1",))
    assert updated.template_context == make_immutable(
        {
            "b": 3,
            "ctx": "ctx",
        }
    )
