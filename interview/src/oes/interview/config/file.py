"""Config file loading."""
import os
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import ContextManager, Union

from ruamel.yaml import YAML

_working_dir_ctx: ContextVar[Path] = ContextVar(
    "_working_dir_ctx", default=Path(os.getcwd())
)


def resolve_config_path(path: Union[str, Path]) -> ContextManager[Path]:
    """Resolve a path to a config file.

    Returns:
        A context manager that sets the new working directory.
    """
    cur_dir = _working_dir_ctx.get()
    resolved_path = cur_dir / Path(path)
    new_dir = resolved_path if resolved_path.is_dir() else resolved_path.parent

    @contextmanager
    def manager():
        token = _working_dir_ctx.set(new_dir)
        try:
            yield resolved_path
        finally:
            _working_dir_ctx.reset(token)

    return manager()


_yaml = YAML(typ="safe")


def load_config_file(path: Union[str, Path]) -> object:
    """Load a config file."""
    with Path(path).open("rt") as f:
        doc = _yaml.load(f)

    return doc
