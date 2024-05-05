"""Missing value resolution."""

from collections.abc import Iterable, Mapping, Sequence, Set

from oes.interview.input.question import QuestionTemplate
from oes.interview.logic.proxy import make_proxy
from oes.interview.logic.types import ValuePointer
from oes.utils.logic import evaluate
from oes.utils.template import TemplateContext


def index_question_templates_by_path(
    question_templates: Iterable[tuple[str, QuestionTemplate]]
) -> dict[Sequence[str | int], tuple[tuple[str, QuestionTemplate], ...]]:
    """Index :class:`QuestionTemplate` objects by the value paths they provide."""
    index = {}
    for id, question_template in question_templates:
        for path in question_template.provides:
            cur = index.get(path, ())
            index[path] = (*cur, (id, question_template))
    return index


def index_question_templates_by_indirect_path(
    question_templates: Iterable[tuple[str, QuestionTemplate]]
) -> dict[
    Sequence[str | int],
    tuple[tuple[str, Set[Sequence[str | int | ValuePointer]], QuestionTemplate], ...],
]:
    """Index :class:`QuestionTemplate` objects by the indirect value paths provided."""
    index = {}
    for id, question_template in question_templates:
        for path in question_template.provides_indirect:
            prefix = _get_path_prefix(path)
            cur = index.get(prefix, ())
            index[prefix] = (
                *cur,
                (id, question_template.provides_indirect, question_template),
            )
    return index


def get_question_template_providing_path(
    path: Sequence[str | int],
    context: TemplateContext,
    skip_ids: Set[str],
    index: Mapping[Sequence[str | int], Sequence[tuple[str, QuestionTemplate]]],
) -> tuple[str, QuestionTemplate] | None:
    """Get a :class:`QuestionTemplate` that provides a value at ``path``."""
    ctx = make_proxy(context)
    templates = index.get(path, ())
    for id, question_template in templates:
        if id not in skip_ids and evaluate(question_template.when, ctx):
            return id, question_template


def get_question_template_providing_indirect_path(
    path: Sequence[str | int],
    context: TemplateContext,
    skip_ids: Set[str],
    index: Mapping[
        Sequence[str | int],
        Sequence[tuple[str, Set[Sequence[str | int | ValuePointer]], QuestionTemplate]],
    ],
) -> tuple[str, QuestionTemplate] | None:
    """Get a :class:`QuestionTemplate` that provides a value at ``path``."""
    ctx = make_proxy(context)
    cur_path = path[:-1]
    while True:
        templates = index.get(cur_path, ())
        for id, provides, question_template in templates:
            if (
                id not in skip_ids
                and evaluate(question_template.when, ctx)
                and any(_evaluate_path(p, ctx) == path for p in provides)
            ):
                return id, question_template
        if not cur_path:
            return
        cur_path = cur_path[:-1]


def _get_path_prefix(path: Sequence[str | int | ValuePointer]) -> Sequence[str | int]:
    prefix = []
    for p in path:
        if isinstance(p, (int, str)):
            prefix.append(p)
        else:
            break
    return tuple(prefix)


def _evaluate_path(
    path: Sequence[str | int | ValuePointer], ctx: TemplateContext
) -> Sequence[str | int]:
    return tuple(p.evaluate(ctx) if not isinstance(p, (str, int)) else p for p in path)
