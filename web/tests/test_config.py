from oes.web.config import get_config


def test_load():
    config = get_config("events.example.yml")
    assert config.events["example-event"].id == "example-event"
