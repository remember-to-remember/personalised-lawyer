""" Module for library functions. """

import argparse
import dataclasses
import json
import logging
import os
from datetime import UTC, datetime
from enum import StrEnum

import structlog
from pydantic.dataclasses import dataclass
from structlog import get_logger

from frontend.app import config


@dataclass
class CLIArgs:
    """Class for command line interface (cli) arguments."""

    debug_mode: bool = False
    chat_app_port: int = 8000
    chat_app_base_url_path: str = "/personal-ai-assistant"


def parse_cli_args_with_defaults() -> CLIArgs:
    """Parse cli arguments with defaults."""

    logger = get_logger()
    logger.info("Starting parse cli arguments with defaults")

    parser = argparse.ArgumentParser(description="CLI arguments")
    parser.add_argument(
        "--debug-mode", help="Enable debug mode logging: false (default)"
    )
    parser.add_argument("--chat-app-port", help="Chat app port: 8000 (default)")
    parser.add_argument(
        "--chat-app-base-url-path",
        help="Chat app base url path: '/personal-ai-assistant' (default)",
    )
    args = parser.parse_args()
    logger.info("Passed cli arguments", args=args)

    cli_args = {
        "debug_mode": json.loads(args.debug_mode) if args.debug_mode else None,
        "chat_app_port": args.chat_app_port if args.chat_app_port else None,
        "chat_app_base_url_path": (
            args.chat_app_base_url_path if args.chat_app_base_url_path else None
        ),
    }
    result = CLIArgs(
        **{arg: value for arg, value in cli_args.items() if value is not None}
    )

    logger.info("Completed parse cli arguments with defaults", result=result)
    return result


@dataclass
class EnvVars:
    """Class for environment variables."""

    auth0_client_id: str = None
    auth0_domain: str = None


def parse_env_vars_with_defaults() -> EnvVars:
    """Parse environment variables with defaults."""

    logger = get_logger()
    logger.info("Starting parse environment variables with defaults")

    env_vars = {
        "auth0_client_id": os.getenv("AUTH0_CLIENT_ID"),
        "auth0_domain": os.getenv("AUTH0_DOMAIN"),
    }
    result = EnvVars(
        **{env: value for env, value in env_vars.items() if value is not None}
    )
    logger.debug("Parsed environment variables", result=result)

    logger.info("Completed parse environment variables with defaults")
    return result


def parse_strenum_from_string(enum_type: StrEnum, value: str) -> any:
    """Parse string enum from string value."""

    logger = get_logger().bind(enum_type=enum_type, value=value)
    logger.info("Starting parse string enum from string value")

    if (
        (enum_type is None or not issubclass(enum_type, StrEnum))
        or value is None
        or value.strip() == ""
    ):
        logger.warning(
            "Unable to parse string enum from string value as it is not proper"
        )
        return None

    uppercase_value = value.upper().strip()
    result = None
    if hasattr(enum_type, uppercase_value):
        result = enum_type[uppercase_value]
    else:
        logger.warning(
            "Unable to parse string enum from string value as it is not found"
        )

    logger.info(
        "Completed parse string enum from string value",
        result=result,
    )
    return result


def configure_global_logging_level(debug_mode) -> logging.Logger:
    """Configure global logging level."""

    logger = get_logger().bind(debug_mode=debug_mode)
    logger.info("Starting configure global logging level")

    logging_level = logging.DEBUG if debug_mode else logging.INFO
    structlog.configure_once(
        wrapper_class=structlog.make_filtering_bound_logger(logging_level),
    )
    if debug_mode:
        logger.debug("Global logging level is set as DEBUG")
    else:
        logger.info("Global logging level is set as INFO")

    logger.info("Completed configure global logging level")


def log_config_settings(conf: config.Config) -> None:
    """Log configuration settings in debug mode."""

    logger = get_logger()
    logger.debug("Starting log configuration settings in debug mode")

    for key, value in dataclasses.asdict(conf).items():
        logger.debug(key, value=str(value))

    logger.debug("Completed log configuration settings in debug mode")


def now_utc() -> datetime:
    """Datetime now in UTC."""

    return datetime.now(UTC)
