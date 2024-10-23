from oes.web.config import get_config


def test_load_config():
    config = get_config("events.example.yml")
    event = config.events["example-event"]
    assert event.id == "example-event"
