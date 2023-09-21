"""Test utilities."""
import httpx


def get_mock_http_client(handler) -> httpx.AsyncClient:
    """Get a mock httpx client."""
    transport = httpx.MockTransport(handler)
    return httpx.AsyncClient(transport=transport)
