from oes.interview.config.interview import load_interviews
from oes.interview.interview import Interview
from oes.interview.serialization import converter


def test_load_interviews():
    interviews = load_interviews(converter, "tests/test_data/interviews.yml")
    assert len(interviews) == 4
    assert isinstance(interviews["interview1"], Interview)
