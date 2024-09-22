""" Module for configuration settings. """

from pydantic.dataclasses import dataclass


@dataclass
class Config:
    """Class for storing configuration settings."""

    # cli args
    debug_mode: bool

    # app
    chat_app_port: int
    chat_app_base_url_path: str

    # auth0
    auth0_client_id: str
    auth0_domain: str


CONFIG: Config = None
