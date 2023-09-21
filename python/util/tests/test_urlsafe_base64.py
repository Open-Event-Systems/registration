from oes.util.urlsafe_base64 import urlsafe_b64decode, urlsafe_b64encode


def test_urlsafe_base64_encode():
    assert urlsafe_b64encode(b"example") == "ZXhhbXBsZQ"


def test_urlsafe_base64_decode():
    assert urlsafe_b64decode("ZXhhbXBsZQ") == b"example"
