import logging
import sys
from pathlib import Path

import typed_settings as ts
import uvicorn
from attrs import frozen
from blacksheep import Application
from loguru import logger
from oes.interview.config.interview import load_interviews
from oes.interview.serialization import converter
from oes.interview.server.app import make_app
from oes.interview.server.settings import load_settings
from oes.interview.variables.env import jinja2_env
from oes.template import set_jinja2_env
from oes.util.logging import InterceptHandler


@frozen
class Args:
    """Command line arguments."""

    debug: bool = ts.option(default=False, help="Enable debug output")
    reload: bool = ts.option(default=False, help="Use reloader")
    bind: str = ts.option(default="0.0.0.0", help="Address to bind to")
    port: int = ts.option(default=8001, help="Port to listen on")
    config: Path = ts.option(default=Path("config.yml"), help="Config file")
    prefix: str = ts.option(default="", help="URL prefix")
    workers: int = ts.option(default=1, help="Number of worker processes")


@ts.cli(Args, ())
def main(args: Args):
    """Main entry point for the console script."""
    _setup_logging(args.debug)

    uvicorn.run(
        app="oes.interview.server.run:_get_app",
        factory=True,
        host=args.bind,
        port=args.port,
        root_path=args.prefix,
        reload=args.reload,
        workers=args.workers,
        log_config=None,
        log_level=logging.DEBUG if args.debug else None,
    )


@ts.cli(Args, ())
def _get_app(args: Args) -> Application:
    _setup_logging(args.debug)

    settings = load_settings(Path(args.config))
    with set_jinja2_env(jinja2_env):
        interview_config = load_interviews(converter, settings.interview_config)
    return make_app(settings, interview_config)


def _setup_logging(debug: bool):
    logger.remove()
    logger.add(sys.stderr, level=logging.DEBUG if debug else logging.INFO)
    logging.basicConfig(
        handlers=[InterceptHandler()],
        level=logging.DEBUG if debug else logging.INFO,
        force=True,
    )
