import os

from alembic.command import upgrade
from alembic.config import Config
from structlog import get_logger

from backend.api.sql_migrations.insert_scripts import caller


def run_db_migrations(connection_string: str, debug_mode: bool) -> None:
    """Run db migrations"""

    logger = get_logger()
    logger.info("Starting run db migrations")

    # retrieves the directory that *this* file is in
    migrations_dir = os.path.dirname(os.path.realpath(__file__))
    # this assumes the alembic.ini is also contained in this same directory
    config_file = os.path.join(migrations_dir, "alembic.ini")
    config = Config(file_=config_file)
    if connection_string and str.strip(connection_string) != "":
        config.set_main_option("sqlalchemy.url", connection_string.replace("%", "%%"))

    # upgrade the database to the latest revision
    upgrade(config, "head")

    # insert data into the database
    caller.insert_callers(connection_string, debug_mode)

    logger.info("Completed run db migrations")
