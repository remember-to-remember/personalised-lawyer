""" Module for command line interface (cli). """

import dataclasses

from structlog import get_logger

from backend.api import config, provider
from backend.api.data_repository import Caller
from backend.api.entities import Chat, ChatInputModel
from backend.api.lib import (
    configure_global_logging_level,
    log_config_settings,
    parse_cli_args_with_defaults,
    parse_env_vars_with_defaults,
)
from backend.api.provider import configure_providers


def get_caller(sub: str):
    """Get caller."""

    logger = get_logger().bind(sub=sub)
    logger.info("Starting get caller")

    caller = provider.PROVIDERS.data_repository.load_caller(sub)

    logger.info("Completed get caller")
    return caller


def process_chat(chat_input: ChatInputModel, caller: Caller) -> Chat:
    """Process chat."""

    logger = get_logger().bind(
        job_request=(
            chat_input.model_dump(
                exclude=chat_input.get_exclude_fields_for_logging(
                    chat_input.request_content_type
                )
            )
            if chat_input
            else None
        ),
        caller=(
            {
                k: str(v)
                for k, v in caller.__dict__.items()
                if k not in Caller.get_exclude_fields_for_logging()
            }
            if caller
            else None
        ),
    )
    logger.info("Starting process chat")

    chat_input = Chat(**chat_input.model_dump())
    chat_input.caller_id = caller.caller_id
    chat_output = provider.PROVIDERS.inference_provider_wrapper.request_for_inference()

    # provider.PROVIDERS.data_repository.save_job(chat_output, caller=caller)

    logger.info("Completed process chat")
    return chat_output


def init() -> None:
    """Entry point if called as an executable."""

    logger = get_logger()
    logger.info("Starting init from main")

    # set configuration based on environment variables and cli arguments
    cli_args = parse_cli_args_with_defaults()
    env_vars = parse_env_vars_with_defaults()
    all_values = dataclasses.asdict(env_vars) | dataclasses.asdict(cli_args)
    config.CONFIG = config.Config(**all_values)
    configure_global_logging_level(config.CONFIG.debug_mode)
    log_config_settings(config.CONFIG)

    # configure providers based on the above configuration
    configure_providers()

    logger.info("Completed init from main")


if __name__ == "__main__":
    init()
