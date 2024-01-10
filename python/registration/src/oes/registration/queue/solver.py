"""Queue solver."""
from collections.abc import Iterator, Mapping, Sequence, Set
from uuid import UUID

import numpy as np
import pyomo.environ as pyo
from attrs import define
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


@define(eq=False)
class StationInfo:
    """Station info struct."""

    id: str
    slots: int
    intercept: float
    coefs: Mapping[str, float]
    wait_time: float
    tags: Set[str]


@define(eq=False)
class QueueItemInfo:
    """Queue item info struct."""

    id: UUID
    priority: int
    tags: Set[str]
    features: Mapping[str, float]

    def can_use_station(self, station: StationInfo) -> bool:
        return station.tags >= self.tags

    def get_service_time(self, station: StationInfo) -> float:
        return station.intercept + sum(
            station.coefs.get(f, 0) * c for f, c in self.features.items()
        )


def solve_queue(
    features: Sequence[str],
    stations: Sequence[StationInfo],
    items: Sequence[QueueItemInfo],
) -> dict[UUID, str]:
    """Solve queue assignments."""
    stations = [s for s in stations if s.slots > 0]
    model = _build_queue_model(features, stations, items)
    model.maximize_assignments.deactivate()
    model.minimize_service_time_increase.deactivate()
    model.num_non_empty_stations_constraint.deactivate()
    model.num_assignments_constraint.deactivate()

    solver = pyo.SolverFactory("cbc")
    solver.solve(model)

    num_non_empty_stations = sum(
        int(pyo.value(var)) for var in model.station_not_empty.values()
    )

    model.maximize_non_empty_stations.deactivate()
    model.maximize_assignments.activate()
    model.num_non_empty_stations = num_non_empty_stations
    model.num_non_empty_stations_constraint.activate()

    solver.solve(model)

    num_assignments = sum(
        int(pyo.value(var)) for var in model.assignment_values.values()
    )

    model.maximize_assignments.deactivate()
    model.minimize_service_time_increase.activate()
    model.num_assignments_constraint.activate()
    model.num_assignments = num_assignments

    solver.solve(model)

    results = {}
    for (station, slot, item), var in model.assignments.items():
        if pyo.value(var) == 1:
            results[item.id] = station.id

    return results


def _build_queue_model(
    features: Sequence[str],
    stations: Sequence[StationInfo],
    items: Sequence[QueueItemInfo],
) -> pyo.ConcreteModel:
    model = pyo.ConcreteModel()
    model.features = pyo.Set(initialize=features)
    model.stations = pyo.Set(initialize=stations)
    model.queue_items = pyo.Set(initialize=items)

    model.station_slots = pyo.Set(dimen=2, initialize=_init_station_slots)
    model.valid_assignments = pyo.Set(dimen=3, initialize=_init_valid_assignments)

    model.assignments = pyo.Var(model.valid_assignments, domain=pyo.Boolean)
    model.assignment_values = pyo.Expression(
        model.valid_assignments, rule=_init_assignment_values
    )

    model.station_not_empty = pyo.Var(model.stations, domain=pyo.Boolean)
    model.station_not_empty_constraint = pyo.Constraint(
        model.stations, rule=_init_station_not_empty_constraint
    )
    model.num_non_empty_stations = pyo.Param(
        domain=pyo.Integers, mutable=True, default=0
    )
    model.num_non_empty_stations_constraint = pyo.Constraint(
        expr=pyo.summation(model.station_not_empty) >= model.num_non_empty_stations
    )

    model.item_constraint = pyo.Constraint(
        model.queue_items, rule=_init_item_constraint
    )
    model.slot_constraint = pyo.Constraint(
        model.station_slots, rule=_init_slot_constraint
    )

    model.service_times = pyo.Expression(model.valid_assignments, rule=_service_time)
    model.station_service_time_increase = pyo.Expression(
        model.stations, rule=_station_service_time_increase
    )

    model.maximize_non_empty_stations = pyo.Objective(
        expr=pyo.summation(model.station_not_empty, index=model.stations),
        sense=pyo.maximize,
    )

    model.maximize_assignments = pyo.Objective(
        expr=pyo.summation(model.assignment_values, index=model.valid_assignments),
        sense=pyo.maximize,
    )

    model.num_assignments = pyo.Param(domain=pyo.Integers, mutable=True, default=0)
    model.num_assignments_constraint = pyo.Constraint(
        expr=pyo.summation(model.assignment_values, index=model.valid_assignments)
        == model.num_assignments,
    )

    model.minimize_service_time_increase = pyo.Objective(
        expr=pyo.summation(model.station_service_time_increase, index=model.stations),
        sense=pyo.minimize,
    )

    return model


def _init_station_slots(model):
    for station in model.stations:
        for i in range(station.slots):
            yield (station, i)


def _init_valid_assignments(model):
    for station in model.stations:
        for item in model.queue_items:
            if item.can_use_station(station):
                yield from ((station, slot, item) for slot in range(station.slots))


def _init_assignment_values(model, station, slot, item):
    return model.assignments[station, slot, item] * item.priority


def _init_item_constraint(model, item):
    vars = []
    for station, slot in model.station_slots:
        if (station, slot, item) in model.valid_assignments:
            vars.append(model.assignments[station, slot, item])
    if not vars:
        return pyo.Constraint.Skip
    return pyo.quicksum(vars) <= 1


def _init_slot_constraint(model, station, slot):
    vars = []
    for item in model.queue_items:
        if (station, slot, item) in model.valid_assignments:
            vars.append(model.assignments[station, slot, item])
    if len(vars) == 0:
        return pyo.Constraint.Feasible
    return pyo.quicksum(vars) <= 1


def _init_station_not_empty_constraint(model, station):
    vars = []
    cur_count = 1 if station.wait_time > 0 else 0
    for slot in range(station.slots):
        for item in model.queue_items:
            if (station, slot, item) in model.valid_assignments:
                vars.append(model.assignments[station, slot, item])
    return model.station_not_empty[station] <= pyo.quicksum(vars) + cur_count


def _service_time(model, station, slot, item):
    return item.get_service_time(station) * model.assignments[station, slot, item]


def _station_service_time_increase(model, station):
    exprs = []
    for slot in range(station.slots):
        for item in model.queue_items:
            if (station, slot, item) in model.valid_assignments:
                exprs.append(model.service_times[station, slot, item])

    sum_ = pyo.quicksum(exprs)
    base = max(station.wait_time, 1.0)
    return sum_ / base
