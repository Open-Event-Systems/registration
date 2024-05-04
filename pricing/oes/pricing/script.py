"""Pricing script module."""

import asyncio
import functools
import os
import subprocess
from collections.abc import Callable, Coroutine, Sequence
from pathlib import Path
from threading import Semaphore

from cattrs.preconf.orjson import make_converter
from oes.pricing.config import Config
from oes.pricing.models import PricingRequest, PricingResult

_max_processes = os.cpu_count() or 2
_process_sem = Semaphore(_max_processes)

_converter = make_converter()


async def get_scripts(
    config: Config, request: PricingRequest
) -> Sequence[Callable[[Config, PricingRequest], Coroutine[None, None, PricingResult]]]:
    """Get pricing scripts."""
    event_config = config.events.get(request.cart.event_id)
    if not event_config:
        raise ValueError(f"No config for event: {request.cart.event_id}")
    path = event_config.script_dir
    if not path:
        return ()
    loop = asyncio.get_running_loop()
    scripts = await loop.run_in_executor(None, _get_scripts, path)
    return [functools.partial(_async_run_script, s) for s in scripts]


def _get_scripts(path: Path) -> list[Path]:
    return sorted(p for p in path.iterdir() if _is_script(p))


def _is_script(path: Path) -> bool:
    return path.is_file() and os.access(path, os.X_OK)


async def _async_run_script(
    path: Path, _config: Config, request: PricingRequest
) -> PricingResult:
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, _run_script, path, request)
    return result


def _run_script(path: Path, request: PricingRequest) -> PricingResult:
    req_data = _converter.dumps(request)
    with _process_sem:
        res = subprocess.run([path], input=req_data, stdout=subprocess.PIPE)
    return _converter.loads(res.stdout, PricingResult)
