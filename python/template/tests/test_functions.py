from datetime import date

import pytest

from oes.template import Template
from oes.template.functions import age_filter, date_filter


@pytest.mark.parametrize(
    "value, expected",
    [
        ("2000-01-01", date(2000, 1, 1)),
        ("2004-02-28", date(2004, 2, 28)),
        (date(2020, 1, 1), date(2020, 1, 1)),
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
