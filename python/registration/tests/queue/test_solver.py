import random
from datetime import timedelta

import pytest
from oes.registration.queue.entities import QueueItemEntity
from oes.registration.queue.solver import solve_features
from oes.util import get_now

features = ("a", "b", "c")


def make_item():
    now = get_now()
    features = {
        "a": random.random(),
        "b": 1 + 2 * random.random(),
        "c": 1 if random.random() >= 0.5 else 0,
    }

    dur = 10 * features["a"] + 3 * features["b"] + 5 * features["c"] + 1.5
    end = now + timedelta(seconds=dur)

    return QueueItemEntity(
        complete=True,
        success=True,
        date_created=now,
        date_completed=end,
        data={"priority": 1, "tags": frozenset(), "features": features},
    )


def test_solve_features():
    examples = [make_item() for _ in range(1000)]
    result = solve_features(features, examples)
    assert result == (
        pytest.approx(1.5),
        {
            "a": pytest.approx(10.0),
            "b": pytest.approx(3.0),
            "c": pytest.approx(5.0),
        },
    )
