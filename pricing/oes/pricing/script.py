"""Pricing script module."""

import asyncio
import os
import subprocess
from pathlib import Path
from threading import Semaphore

from cattrs.preconf.orjson import make_converter
from oes.pricing.models import PricingRequest

_max_processes = os.cpu_count() or 2
_process_sem = Semaphore(_max_processes)

_converter = make_converter()


async def run_scripts(path: Path, request: PricingRequest) -> PricingRequest:
    """Run pricing scripts."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _run_scripts, path, request)


def _run_scripts(path: Path, request: PricingRequest) -> PricingRequest:
    cur_request = request
    for script in _get_scripts(path):
        cur_request = _run_script(script, cur_request)
    return cur_request


def _get_scripts(path: Path) -> list[Path]:
    return sorted(p for p in path.iterdir() if _is_script(p))


def _is_script(path: Path) -> bool:
    return path.is_file() and os.access(path, os.X_OK)


def _run_script(path: Path, request: PricingRequest):
    req_data = _converter.dumps(request)
    with _process_sem:
        res = subprocess.run([path], input=req_data, stdout=subprocess.PIPE)
    return _converter.loads(res.stdout, PricingRequest)
