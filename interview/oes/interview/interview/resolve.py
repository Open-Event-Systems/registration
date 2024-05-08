"""Missing value resolution."""

from __future__ import annotations

from collections.abc import Sequence, Set
from typing import TYPE_CHECKING, Any

from attrs import define, field
from oes.interview.input.question import Question, QuestionTemplate
from oes.interview.interview.error import InterviewError
from oes.interview.logic.proxy import ProxyLookupError, make_proxy
from oes.interview.logic.undefined import UndefinedError
from oes.utils.logic import evaluate
from oes.utils.template import TemplateContext
from typing_extensions import Self

if TYPE_CHECKING:
    from oes.interview.interview.interview import InterviewContext


# def index_question_templates_by_indirect_path(
#     question_templates: Iterable[tuple[str, QuestionTemplate]]
# ) -> dict[
#     Sequence[str | int],
#     tuple[tuple[str, Set[Sequence[str | int | ValuePointer]]], ...],
# ]:
#     """Index :class:`QuestionTemplate` objects by the indirect value paths
#     provided."""
#     index = {}
#     for id, question_template in question_templates:
#         for path in question_template.provides_indirect:
#             prefix = _get_path_prefix(path)
#             cur = index.get(prefix, ())
#             index[prefix] = (
#                 *cur,
#                 (id, question_template.provides_indirect),
#             )
#     return index


@define
class Resolver:
    """Missing value resolver."""

    interview_context: InterviewContext
    skip_ids: Set[str]
    result: tuple[str, QuestionTemplate, Question] = field(init=False)

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_typ: type[BaseException] | None,
        exc_val: BaseException | None,
        tb: Any,
    ) -> bool:
        if isinstance(exc_val, (ProxyLookupError, UndefinedError)):
            path = (*exc_val.path, exc_val.key)
            self.result = resolve_question_providing_path(
                path, self.interview_context, self.skip_ids
            )
            return True
        return False


def resolve_undefined_values(
    interview_context: InterviewContext,
    skip_ids: Set[str] = frozenset(),
) -> Resolver:
    """Return a context manager to resolve any undefined value exceptions."""
    return Resolver(interview_context, skip_ids)


def resolve_question_providing_path(
    path: Sequence[str | int],
    interview_context: InterviewContext,
    skip_ids: Set[str] = frozenset(),
) -> tuple[str, QuestionTemplate, Question]:
    """Get a :class:`Question` providing a value at ``path``."""
    proxy_ctx = make_proxy(interview_context.state.template_context)
    selected = _resolve_question(path, interview_context, skip_ids, proxy_ctx)
    # if selected is None:
    #     selected = _resolve_question_indirect(
    #         path, interview_context, skip_ids, proxy_ctx
    #     )
    if selected is None:
        value_str = " -> ".join(repr(v) for v in path)
        raise InterviewError(f"No questions provide value {value_str}")

    return selected


def _resolve_question(
    path: Sequence[str | int],
    interview_context: InterviewContext,
    skip_ids: Set[str],
    ctx: TemplateContext,
) -> tuple[str, QuestionTemplate, Question] | None:
    for id in interview_context.path_index.get(path, ()):
        if id in interview_context.state.answered_question_ids or id in skip_ids:
            continue
        with resolve_undefined_values(  # noqa: NEW100
            interview_context, skip_ids | {id}
        ) as resolver:
            question_template = interview_context.question_templates[id]
            if not evaluate(question_template.when, ctx):
                continue
            return _render_question(id, question_template, ctx)
        return resolver.result
    return None


# def _resolve_question_indirect(
#     path: Sequence[str | int],
#     interview_context: InterviewContext,
#     skip_ids: Set[str],
#     ctx: TemplateContext,
# ) -> tuple[str, Question] | None:
#     for id, provides in _get_question_templates_providing_indirect_path(
#         path, interview_context.indirect_path_index
#     ):
#         if id in interview_context.state.answered_question_ids or id in skip_ids:
#             continue
#         with resolve_undefined_values(  # noqa: NEW100
#             interview_context, skip_ids | {id}
#         ) as resolver:
#             # TODO: need to check if this results in spurious ask steps...
#             if not any(_evaluate_path(p, ctx) == path for p in provides):
#                 continue
#             question_template = interview_context.question_templates[id]
#             if not evaluate(question_template.when, ctx):
#                 continue
#             return _render_question(id, question_template, ctx)
#         return resolver.result
#     return None


def _render_question(
    id: str,
    template: QuestionTemplate,
    ctx: TemplateContext,
) -> tuple[str, QuestionTemplate, Question]:
    question = template.get_question(ctx)
    return id, template, question


# def _get_question_templates_providing_indirect_path(
#     path: Sequence[str | int],
#     index: Mapping[
#         Sequence[str | int],
#         Sequence[tuple[str, Set[Sequence[str | int | ValuePointer]]]],
#     ],
# ) -> Generator[tuple[str, Set[Sequence[str | int | ValuePointer]]], None, None]:
#     cur_path = path[:-1]
#     while True:
#         templates = index.get(cur_path, ())
#         yield from templates
#         if not cur_path:
#             return
#         cur_path = cur_path[:-1]


# def _get_path_prefix(path: Sequence[str | int | ValuePointer]) -> Sequence[str | int]:
#     prefix = []
#     for p in path:
#         if isinstance(p, (int, str)):
#             prefix.append(p)
#         else:
#             break
#     return tuple(prefix)


# def _evaluate_path(
#     path: Sequence[str | int | ValuePointer], ctx: TemplateContext
# ) -> Sequence[str | int]:
#     return tuple(p.evaluate(ctx) if not isinstance(p,(str, int)) else p for p in path)
