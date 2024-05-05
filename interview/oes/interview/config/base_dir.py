"""Working directory context."""

from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path

_base_dir: ContextVar[Path] = ContextVar("_base_dir", default=Path.cwd())


@contextmanager
def set_base_directory(path: Path | str) -> Generator[Path | str, None, None]:
    """Set the base directory for relative config files."""
    cur_base = _base_dir.get()
    new_base = (cur_base / path).resolve()
    token = _base_dir.set(new_base)
    try:
        yield new_base
    finally:
        _base_dir.reset(token)
