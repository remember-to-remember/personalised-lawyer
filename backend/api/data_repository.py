""" Module for data repository. """

from abc import ABC

from pydantic import ValidationError
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, exc
from structlog import get_logger

from backend.api import config
from backend.api.entities import Caller, CallerModel
from backend.api.sql_migrations import run


class DataRepository(ABC):
    """Class for data repository."""

    engine: Engine = None

    def __init__(self, connection_string: str, echo: bool, run_db_migrations: bool):
        if run_db_migrations:
            run.run_db_migrations(connection_string, echo)
        self.engine = create_engine(connection_string, echo=echo)

    def load_caller(self, api_key: str) -> Caller:
        """Load caller from data repository."""

        logger = get_logger().bind(api_key=api_key)
        logger.info("Starting load caller")

        with Session(self.engine) as session:
            try:
                caller = session.query(Caller).filter_by(api_key=api_key).one_or_none()
                CallerModel.model_validate(caller)
            except ValidationError as error:
                logger.error(
                    error,
                    stack_info=config.CONFIG.debug_mode,
                    exc_info=config.CONFIG.debug_mode,
                )
                raise None
            except exc.MultipleResultsFound as error:
                logger.error(
                    error,
                    stack_info=config.CONFIG.debug_mode,
                    exc_info=config.CONFIG.debug_mode,
                )
                return None

        logger.info("Completed load caller")
        return caller
