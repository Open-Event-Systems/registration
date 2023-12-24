import random
import uuid
from datetime import timedelta

import pytest
from oes.registration.queue.entities import QueueItemEntity
from oes.registration.queue.solver import (
    QueueItemInfo,
    StationInfo,
    solve_features,
    solve_queue,
)
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


def test_simple_model():
    e1 = QueueItemInfo(id=uuid.uuid4(), priority=1, tags={"a"}, features={"a": 1})
    e2 = QueueItemInfo(id=uuid.uuid4(), priority=1, tags={"b"}, features={"a": 1})
    s1 = StationInfo(
        id="1", slots=1, intercept=0, coefs={"a": 1.0}, wait_time=0, tags={"a", "b"}
    )
    s2 = StationInfo(
        id="2", slots=1, intercept=0, coefs={"a": 1.0}, wait_time=0, tags={"a"}
    )

    res = solve_queue(("a",), (s1, s2), (e1, e2))
    assert res == {
        e1.id: "2",
        e2.id: "1",
    }


def test_model_chooses_fastest_station():
    e1 = QueueItemInfo(id=uuid.uuid4(), priority=1, tags={"a"}, features={"a": 0})

    e2 = QueueItemInfo(id=uuid.uuid4(), priority=1, tags={"a"}, features={"a": 1})

    s1 = StationInfo(
        id="1", slots=1, intercept=5, coefs={"a": 10.0}, wait_time=0, tags={"a"}
    )

    s2 = StationInfo(
        id="2", slots=1, intercept=5, coefs={"a": 5.0}, wait_time=0, tags={"a"}
    )

    res = solve_queue(("a",), (s1, s2), (e1, e2))

    assert res == {
        e1.id: "1",
        e2.id: "2",
    }


def test_model_chooses_fastest_station_non_empty():
    e1 = QueueItemInfo(id=uuid.uuid4(), priority=1, tags={"a"}, features={"a": 1})

    s1 = StationInfo(
        id="1", slots=1, intercept=5, coefs={"a": 10.0}, wait_time=10, tags={"a"}
    )

    s2 = StationInfo(
        id="2", slots=1, intercept=5, coefs={"a": 5.0}, wait_time=10, tags={"a"}
    )

    res = solve_queue(("a",), (s1, s2), (e1,))

    assert res == {
        e1.id: "2",
    }


def test_model_minimizes_service_time_increase():
    e1 = QueueItemInfo(id=uuid.uuid4(), priority=1, tags={"a"}, features={"a": 0})

    e2 = QueueItemInfo(id=uuid.uuid4(), priority=1, tags={"a"}, features={"a": 1})

    s1 = StationInfo(
        id="1", slots=1, intercept=1, coefs={"a": 10.0}, wait_time=10, tags={"a"}
    )

    s2 = StationInfo(
        id="2", slots=1, intercept=1, coefs={"a": 10.0}, wait_time=0, tags={"a"}
    )

    res = solve_queue(("a",), (s1, s2), (e1, e2))
    assert res == {
        e1.id: "2",
        e2.id: "1",
    }


def test_model_chooses_fastest_station_minimizing_time_increase():
    e1 = QueueItemInfo(id=uuid.uuid4(), priority=1, tags={"a"}, features={"a": 0})

    e2 = QueueItemInfo(id=uuid.uuid4(), priority=1, tags={"a"}, features={"a": 1})

    s1 = StationInfo(
        id="1", slots=1, intercept=15, coefs={"a": 10.0}, wait_time=0, tags={"a"}
    )

    s2 = StationInfo(
        id="2", slots=1, intercept=5, coefs={"a": 5.0}, wait_time=0, tags={"a"}
    )

    res = solve_queue(("a",), (s1, s2), (e1, e2))

    assert res == {
        e1.id: "1",
        e2.id: "2",
    }


def test_model_chooses_fastest_station_minimizing_time_increase_initial():
    e1 = QueueItemInfo(id=uuid.uuid4(), priority=1, tags={"a"}, features={"a": 0})

    e2 = QueueItemInfo(id=uuid.uuid4(), priority=1, tags={"a"}, features={"a": 1})

    s1 = StationInfo(
        id="1", slots=1, intercept=15, coefs={"a": 10.0}, wait_time=15, tags={"a"}
    )

    s2 = StationInfo(
        id="2", slots=1, intercept=5, coefs={"a": 5.0}, wait_time=0, tags={"a"}
    )

    res = solve_queue(("a",), (s1, s2), (e1, e2))

    assert res == {
        e1.id: "2",
        e2.id: "1",
    }


def test_model_leaves_no_empty_stations():
    e1 = QueueItemInfo(id=uuid.uuid4(), priority=1, tags={"a"}, features={"a": 0})

    s1 = StationInfo(
        id="1", slots=2, intercept=10, coefs={"a": 10.0}, wait_time=0, tags={"a"}
    )

    s2 = StationInfo(
        id="2", slots=1, intercept=5, coefs={"a": 10.0}, wait_time=5, tags={"a"}
    )

    res = solve_queue(("a",), (s1, s2), (e1,))

    assert res == {
        e1.id: "1",
    }


def test_complex_model():
    e1 = QueueItemInfo(id=uuid.uuid4(), priority=1, tags={"a"}, features={"a": 1})

    e2 = QueueItemInfo(id=uuid.uuid4(), priority=1, tags={"b"}, features={"b": 1})

    e3 = QueueItemInfo(id=uuid.uuid4(), priority=1, tags={"a"}, features={"a": 1})

    e4 = QueueItemInfo(
        id=uuid.uuid4(), priority=1, tags={"a", "b"}, features={"a": 1, "b": 1}
    )

    e5 = QueueItemInfo(id=uuid.uuid4(), priority=1, tags={"b"}, features={"b": 1.5})

    s1 = StationInfo(
        id="1", slots=2, intercept=5, coefs={"a": 5.0}, wait_time=10, tags={"a"}
    )

    s2 = StationInfo(
        id="2",
        slots=2,
        intercept=4,
        coefs={"a": 4.0, "b": 10.0},
        wait_time=8,
        tags={"a", "b"},
    )

    s3 = StationInfo(
        id="3", slots=2, intercept=5, coefs={"b": 10.0}, wait_time=0, tags={"b"}
    )

    s4 = StationInfo(id="4", slots=2, intercept=2, coefs={}, wait_time=0, tags={"c"})

    res = solve_queue(("a",), (s1, s2, s3, s4), (e1, e2, e3, e4, e5))
    assert len(res) == 5
    assert res[e4.id] == "2"
    assert any(v == "3" for v in res.values())
    print("e1 =", res[e1.id])
    print("e2 =", res[e2.id])
    print("e3 =", res[e3.id])
    print("e4 =", res[e4.id])
    print("e5 =", res[e5.id])
