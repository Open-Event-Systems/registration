from datetime import date, datetime, timezone
from unittest.mock import patch

import pytest
from oes.template import Expression, Template
from oes.template.filters import age_filter, date_filter, datetime_filter

_cur_tz = datetime.now().astimezone().tzinfo


@pytest.mark.parametrize(
    "value, expected",
    [
        ("2020-01-01T00:00:00+00:00", datetime(2020, 1, 1, 0, tzinfo=timezone.utc)),
        ("2020-01-01T12:00:00", datetime(2020, 1, 1, 12, tzinfo=_cur_tz)),
        (datetime(2020, 1, 1, 12), datetime(2020, 1, 1, 12)),
        (
            datetime(2020, 1, 1, 12, tzinfo=_cur_tz),
            datetime(2020, 1, 1, 12, tzinfo=_cur_tz),
        ),
        (1577880000, datetime(2020, 1, 1, 12, tzinfo=timezone.utc)),
        (date(2020, 1, 1), datetime(2020, 1, 1, 0, tzinfo=_cur_tz)),
        ("2020-01-01", datetime(2020, 1, 1, 0, tzinfo=_cur_tz)),
    ],
)
def test_datetime_filter(value, expected):
    assert datetime_filter(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("2000-01-01", date(2000, 1, 1)),
        ("2004-02-28", date(2004, 2, 28)),
        (date(2020, 1, 1), date(2020, 1, 1)),
        ("2020-01-01T00:00:00+00:00", date(2020, 1, 1)),
        (1577880000, date(2020, 1, 1)),
    ],
)
def test_date_filter(value, expected):
    assert date_filter(value) == expected


@pytest.mark.parametrize(
    "value, cur, expected",
    [
        (date(2000, 7, 4), date(2010, 7, 4), 10),
        (date(2000, 7, 4), date(2010, 7, 3), 9),
        (date(2000, 7, 4), date(2010, 6, 4), 9),
        (date(2000, 7, 4), date(2010, 8, 4), 10),
        (date(2000, 7, 4), date(2000, 7, 4), 0),
        (date(2000, 7, 4), date(2000, 7, 5), 0),
        ("2005-02-20", "2017-05-02", 12),
    ],
)
def test_age_filter(value, cur, expected):
    assert age_filter(value, cur) == expected


@pytest.mark.parametrize(
    "date1, birth_date, cur_date, expected",
    [
        ("2003-05-15", "2000-10-31", "2020-09-08", "Month: 5, Age: 19"),
        (date(2003, 2, 15), date(2000, 10, 31), date(2020, 11, 5), "Month: 2, Age: 20"),
    ],
)
def test_age_and_date_filters_in_template(date1, birth_date, cur_date, expected):
    tmpl = Template("Month: {{ (date1 | date).month }}, Age: {{ date2 | age(date3) }}")

    res = tmpl.render({"date1": date1, "date2": birth_date, "date3": cur_date})
    assert res == expected


@patch("oes.template.filters.datetime")
def test_today(datetime_mock):
    now = datetime(2023, 1, 1, 12).astimezone()
    datetime_mock.now.return_value = now
    today = now.date()
    expr = Expression("get_today()")
    assert expr.evaluate({}) == today


@patch("oes.template.filters.datetime")
def test_now(datetime_mock):
    now = datetime(2023, 1, 1, 12).astimezone()
    datetime_mock.now.return_value = now
    expr = Expression("get_now()")
    assert expr.evaluate({}) == now