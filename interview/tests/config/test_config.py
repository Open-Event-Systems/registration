from pathlib import Path

import pytest
from cattrs import Converter
from cattrs.preconf.orjson import make_converter
from oes.interview.config.config import load_config
from oes.interview.serialization import configure_converter


@pytest.fixture
def converter():
    converter = make_converter()
    configure_converter(converter)
    return converter


@pytest.mark.parametrize(
    "path, num_interviews",
    [
        ("tests/test_data/configs/config1.yml", 5),
    ],
)
def test_config(path, num_interviews: int, converter: Converter):
    path = Path(path)
    base_dir = path.parent
    cfg = load_config(path, converter)
    interviews = cfg.get_interviews(base_dir, converter)
    assert len(interviews) == num_interviews
