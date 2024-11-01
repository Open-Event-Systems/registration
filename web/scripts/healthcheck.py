"""Health check script."""

import httpx

res = httpx.get("http://localhost:8000/events")
res.raise_for_status()
