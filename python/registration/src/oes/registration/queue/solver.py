"""Queue solver."""
from collections.abc import Iterable, Iterator, Sequence, Set

import numpy as np
import pyomo.environ as pyo
from oes.registration.queue.entities import QueueItemEntity


def solve_features(
    features: Sequence[str],
    data: Sequence[QueueItemEntity],
) -> tuple[float, dict[str, float]]:
    """Get service time coefficients for features.

    Args:
        features: A sequence of feature IDs.
        data: A sequence of completed queue items.

    Returns:
        A pair of a constant time and a mapping of feature IDs to coefficients.
    """
    coef_shape = np.dtype((float, len(features) + 1))
    coefs = np.fromiter(
        _get_coefs(features, data),
        dtype=coef_shape,
        count=len(data),
    )
    durations = np.fromiter(_get_durations(data), dtype=float)
    solution, _, _, _ = np.linalg.lstsq(coefs, durations, rcond=None)
    intercept = solution[0]
    return intercept, dict(zip(features, solution[1:]))


def _get_coefs(
    features: Sequence[str], data: Sequence[QueueItemEntity]
) -> Iterator[Sequence[float]]:
    for item in data:
        item_data = item.get_data()
        coefs = (1.0, *(item_data.features.get(f, 0) for f in features))
        yield coefs


def _get_durations(data: Sequence[QueueItemEntity]) -> Iterator[Sequence[float]]:
    for item in data:
        yield item.duration
