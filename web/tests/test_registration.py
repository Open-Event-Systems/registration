from oes.web.registration import Registration


def test_registration_object():
    r = Registration()
    assert r.id
    assert r.version == 1
    assert r.status == "created"

    r2 = Registration(r)
    assert r2 == r
