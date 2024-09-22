""" Module for sqlite. """

from backend.api import config
from backend.api.data_repository import DataRepository


class SQLite(DataRepository):
    """Class for sqlite."""

    def __init__(self):
        super().__init__(
            config.CONFIG.sqlite_connection_string,
            config.CONFIG.debug_mode,
            config.CONFIG.run_db_migrations,
        )
